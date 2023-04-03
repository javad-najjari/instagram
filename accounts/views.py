import random
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    UserRegistrationSerializer, ProfileSerializer, ListOfFollowersSerializer, ListOfFollowingSerializer,
    EditProfileSerializer, ChangePasswordSerializer, StorySerializer, EditProfilePhotoSerializer,
    ListForSendPostSerializer, UserSuggestionSerializer, UserActivitiesSerializer, GetCodeSerializer
)
from post.serializers import PostListProfileSerializer
from rest_framework import status
from .models import StoryViews, User, Story, Activities, OtpCode
from .paginations import PaginateBy6, PaginateBy10
from utils import send_otp_code, is_user_allowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken
from follow.models import Follow
from rest_framework.generics import ListAPIView, UpdateAPIView, DestroyAPIView
from django.db import connection, reset_queries




class UserRegistrationEmailView(APIView):
    """
    Receive: `username`, `email`, `password`, `password2`.\n
    Remember: User information must be stored in a key named `user_registration_info` for use in the next endpoint.\n
    Then send the `confirmation code` to the user's email.
    """
    
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            random_code = random.randint(100000, 999999)
            OtpCode.objects.create(email=serializer.validated_data['email'], code=random_code)
            send_otp_code(serializer.validated_data['email'], random_code)

            # To request with postman
            request.session['user_registration_info'] = {
                'username': serializer.validated_data['username'],
                'email': serializer.validated_data['email'],
                'password': serializer.validated_data['password']
            }
            return Response({'detail': 'We have sent you a code.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserRegistrationConfirmationView(APIView):
    """
    Receive: `code` and key `user_registration_info`.\n
    Registering the user and returning the `access token` and the `refresh token`.
    """

    serializer_class = GetCodeSerializer

    def post(self, request):

        # Check the code
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        
        # Check user information
        user_registration_info = request.session.get('user_registration_info') or request.data.get('user_registration_info')
        if not user_registration_info:
            return Response({'detail': 'User information is missing or lost.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check the otp code
        try:
            otp_code = OtpCode.objects.get(email=user_registration_info['email'], code=code)
        except OtpCode.DoesNotExist:
            return Response({'detail': 'The code is incorrect.'}, status=status.HTTP_404_NOT_FOUND)

        if not otp_code.is_valid():
            otp_code.delete()
            return Response({'detail': 'The code has expired.'}, status=status.HTTP_404_NOT_FOUND)
        
        otp_code.delete()

        # Create user
        user = User.objects.create_user(
            username=user_registration_info['username'],
            email=user_registration_info['email'],
            password=user_registration_info['password']
        )
        
        request.session.flush()

        tokens = {
            'refresh': str(TokenObtainPairSerializer().get_token(user)),
            'access': str(AccessToken().for_user(user))
        }
        
        return Response({'tokens': tokens}, status=status.HTTP_200_OK)



class ProfileView(APIView):
    """
    Receive: `username`\n
    Returning: `pagination` and `user` information\n
    And also user `posts` if `full_access_to_profile` is true. That's mean:\n
    (requested_user = auth_user) `or` (auth_user is following requested_user) `or` (requested_user account is not private)
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    pagination_class = PaginateBy6

    def get(self, request, username):
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        is_following = Follow.objects.filter(from_user=request.user, to_user=user).exists()
        full_access_to_profile = request.user == user or is_following or not user.private
        profile_serializer = self.serializer_class(
            user, context={'full_access_to_profile': full_access_to_profile, 'request': request}
        )
        context = {'profile': profile_serializer.data}
        
        if full_access_to_profile:
            posts = user.user_posts.all()
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(posts, request)
            posts_serializer = PostListProfileSerializer(result_page, context={'request': request}, many=True)
            context['posts'] = posts_serializer.data
            return paginator.get_paginated_response(context)
        
        return Response(context, status=status.HTTP_200_OK)



class SavedPostsView(ListAPIView):
    """
    The user's `saved posts` are displayed in paginated format (6 posts per page).
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = PostListProfileSerializer
    pagination_class = PaginateBy6

    def get_queryset(self):
        posts = self.request.user.user_saves.select_related('post').all()
        return [post.post for post in posts]
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    


class EditProfileView(APIView):
    """
    Edit user information (except `profile picture`).\n
    Only these fields can be edited: `name` , `website` , `bio` , `gender` , `open_suggestions`.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = EditProfileSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = self.serializer_class(instance=request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EditProfilePhotoView(UpdateAPIView, DestroyAPIView):
    """
    Edit user's `profile photo`. The maximum file size that can be uploaded is `500 KB`.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = EditProfilePhotoSerializer
    http_method_names = ('put', 'delete')

    def get_object(self):
        return self.request.user
    
    def delete(self, request, *args, **kwargs):
        """ If the user has a `profile picture`, it will be deleted. Otherwise, `error 400` will be returned """

        user = self.get_object()
        if user.profile_photo:
            user.profile_photo.delete()
            return Response({'detail': 'Profile photo deleted successfully.'}, status=status.HTTP_200_OK)
        
        return Response(
            {'detail': 'The user does not have a profile photo to delete.'},
            status=status.HTTP_400_BAD_REQUEST
        )



class FollowersView(ListAPIView):
    """
    Receive: `username`\n
    Returning: The list of requested user `followers`. (if you have permission)
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ListOfFollowersSerializer
    pagination_class = PaginateBy10

    def get_queryset(self):
        user = User.objects.get(username=self.kwargs.get('username'))
        if is_user_allowed(self.request.user, user):
            return user.followers.all().order_by('id')
        raise PermissionDenied('You are not allowed to see the list of followers.')



class FollowingView(ListAPIView):
    """
    Receive: `username`\n
    Returning: The list of requested user `following`. (if you have permission)
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ListOfFollowingSerializer
    pagination_class = PaginateBy10

    def get_queryset(self):
        user = User.objects.get(username=self.kwargs.get('username'))
        if is_user_allowed(self.request.user, user):
            return user.following.all().order_by('id')
        raise PermissionDenied('You are not allowed to see the list of following.')



class ChangePasswordView(APIView):
    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.POST)
        if serializer.is_valid():
            if not user.check_password(serializer.data['old_password']):
                return Response(status=status.HTTP_404_NOT_FOUND)
            if serializer.data['password1'] != serializer.data['password2']:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            if user.check_password(serializer.data['password1']):
                return Response(status=status.HTTP_403_FORBIDDEN)
            user.set_password(serializer.data['password1'])
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class StoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        user = User.objects.get(username=username)
        stories = Story.objects.filter(user=user)

        if not stories:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        for story in stories:
            if not StoryViews.objects.filter(user=request.user, story=story).exists():
                all_has_seen = False
        else:
            all_has_seen = True
        
        serializer = StorySerializer(stories, context={'request': request}, many=True)
        value = {'stories': serializer.data, 'all_has_seen': all_has_seen}
        return Response(value, status=status.HTTP_200_OK)


class SeenStoryView(APIView):
    def get(self, request, story_id):
        story = Story.objects.get(id=story_id)
        if request.user != story.user:
            if not StoryViews.objects.filter(user=request.user, story=story).exists():
                StoryViews.objects.create(user=request.user, story=story)


class CreateStoryView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if file:
            f = Story(file=file, user=request.user)
            if f.extension() == 'unacceptable':
                return Response(status=status.HTTP_400_BAD_REQUEST)
            f.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RemoveStoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, story_id):
        story = Story.objects.get(id=story_id)
        if request.user == story.user:
            story.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class FollowView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        auth_user = request.user
        user = get_object_or_404(User, id=user_id)
        if not Follow.objects.filter(from_user=auth_user, to_user=user).exists():
            if not Activities.objects.filter(from_user=auth_user, to_user=user, follow=True).exists():
                if user != auth_user:
                    Activities.objects.create(
                        from_user=auth_user, to_user=user, follow=True
                    )
            Follow.objects.create(from_user=auth_user, to_user=user)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UnFollowView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        auth_user = request.user
        user = get_object_or_404(User, id=user_id)
        if Follow.objects.filter(from_user=auth_user, to_user=user).exists():
            if Activities.objects.filter(from_user=auth_user, to_user=user, follow=True).exists():
                Activities.objects.get(from_user=auth_user, to_user=user, follow=True).delete()
            Follow.objects.get(from_user=auth_user, to_user=user).delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class RemoveFollowerView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if Follow.objects.filter(from_user=user, to_user=request.user).exists():
            Follow.objects.get(from_user=user, to_user=request.user).delete()
            return Response(status=status.HTTP_200_OK)
        return Response(ststus=status.HTTP_404_NOT_FOUND)


class ListForSendPostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        following = user.following.all()
        serializer = ListForSendPostSerializer(following, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSuggestionView(APIView):
    def get(self, request):
        user = request.user
        following = user.following.all()
        users = []
        for following in following:
            for end_user in following.to_user.following.all():
                if not Follow.objects.filter(from_user=user, to_user=end_user.to_user).exists() and end_user.to_user != user:
                    if end_user.to_user not in users:
                        users.append(end_user.to_user)
        final_users = sorted(users, key=lambda x:users.count(x), reverse=True)
        # for item in final_users:
        #     if final_users.count(item) > 1:
        #         final_users.remove(item)
        if len(final_users) > 4:
            final_users = final_users[:5]
        
        serializer = UserSuggestionSerializer(final_users, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserActivities(APIView):
    def get(self, request):
        activity = Activities.objects.filter(to_user=request.user)
        serializer = UserActivitiesSerializer(activity, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

