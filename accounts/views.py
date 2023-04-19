import random
from django.shortcuts import get_object_or_404
from django.db import connection, reset_queries
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    UserRegistrationSerializer, ProfileSerializer, ListOfFollowersSerializer, ListOfFollowingSerializer,
    EditProfileSerializer, ChangePasswordSerializer, StorySerializer, EditProfilePhotoSerializer,
    ListForSendPostSerializer, UserSuggestionSerializer, UserActivitiesSerializer, GetCodeSerializer,
    UserInformationSerializer, SearchUserSerializer
)
from post.serializers import PostListProfileSerializer
from .models import StoryViews, User, Story, Activity, OtpCode
from paginations import PaginateBy6, PaginateBy10
from utils import send_otp_code, is_user_allowed, activity_text_follow
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, TokenError, RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from follow.models import Follow
from rest_framework.generics import ListAPIView, UpdateAPIView, DestroyAPIView




class UserRegistrationEmailView(APIView):
    """
    Receive: `username`, `email`, `password`, `password2`.\n
    Remember: User information must be stored in a key named `user_registration_info` for use in the next endpoint.\n
    Note: The `password` should not be simple, otherwise: Error 402\n
    And then the `confirmation code` will be sent to the user.
    """
    
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                validate_password(serializer.validated_data['password'])
            except:
                return Response('This password is too common', status=402)

            random_code = random.randint(100000, 999999)
            OtpCode.objects.create(email=serializer.validated_data['email'], code=random_code)
            send_otp_code(serializer.validated_data['email'], random_code)

            # To request with postman
            request.session['user_registration_info'] = {
                'username': serializer.validated_data['username'],
                'email': serializer.validated_data['email'],
                'password': serializer.validated_data['password']
            }
            return Response('We have sent you a code.', status=200)
        
        return Response(serializer.errors, status=400)



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
            return Response('User information is missing or lost.', status=400)
        
        # Check the otp code
        try:
            otp_code = OtpCode.objects.get(email=user_registration_info['email'], code=code)
        except OtpCode.DoesNotExist:
            return Response('The code is incorrect.', status=404)

        if not otp_code.is_valid():
            otp_code.delete()
            return Response('The code has expired.', status=404)
        
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
        
        return Response({'tokens': tokens}, status=200)



class CustomizeTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response('Refresh token has expired.', status=410)

        return Response(serializer.validated_data, status=200)



# class CustomTokenVerifyView(TokenVerifyView):
#     def dispatch(self, request, *args, **kwargs):
#         try:
#             self.get_object()
#         except TokenError as e:
#             if str(e) == 'Token is expired':
#                 return Response('Token has expired.', status=411)
#             else:
#                 return Response('Invalid token.', status=401)
#         else:
#             return super().dispatch(request, *args, **kwargs)



# TODO: the access_token must also expire
class LogoutView(APIView):
    """
    Receive: `refresh_tokeh`\n
    Note: The `access token` must be removed from the user header.\n
    Then the user will be logged out.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            RefreshToken(refresh_token).blacklist()
            return Response('Logged out successfully.', status=204)
        except:
            return Response('Token is not valid.', status=400)



class ProfileView(APIView):
    """
    Receive: `username`\n
    Returning: `user` information
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get(self, request, username):
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response('User not found.', status=404)
        
        is_following = Follow.objects.filter(from_user=request.user, to_user=user).exists()
        is_owner = request.user == user
        full_access_to_profile = request.user == user or is_following or not user.private
        profile_serializer = self.serializer_class(
            user, context={'full_access_to_profile': full_access_to_profile, 'is_owner': is_owner, 'request': request}
        )
        return Response(profile_serializer.data, status=200)



class UserProfilePosts(ListAPIView):
    """
    Receive: `username`\n
    Returning: user `posts` if `full_access_to_profile` is true. That's mean:\n
    (requested_user = auth_user) `or` (auth_user is following requested_user) `or` (requested_user account is not private)
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = PostListProfileSerializer
    pagination_class = PaginateBy6

    def list(self, request, *args, **kwargs):
        user = User.objects.filter(username=kwargs.get('username')).first()
        if user is None:
            return Response('User not found.', status=404)

        is_following = Follow.objects.filter(from_user=request.user, to_user=user).exists()
        access_to_posts = request.user == user or is_following or not user.private

        if access_to_posts:
            posts = user.user_posts.all()
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(posts, request)
            posts_serializer = self.serializer_class(result_page, context={'request': request}, many=True)
            return paginator.get_paginated_response(posts_serializer.data)
        return Response("You are not allowed to see this user's posts", status=400)



class SavedPostsView(ListAPIView):
    """
    The user's `saved posts` are displayed in paginated format (6 posts per page).
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = PostListProfileSerializer
    pagination_class = PaginateBy6

    def get_queryset(self):
        posts = self.request.user.user_saves.select_related('post').all().order_by('-created')
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
        return Response(serializer.data, status=200)
    
    def put(self, request):
        serializer = self.serializer_class(instance=request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)



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
            return Response('Profile photo deleted successfully.', status=200)
        
        return Response(
            'The user does not have a profile photo to delete.',
            status=400
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
    """
    Receive: `old_password` , `password1` , `password2`\n
    Conditions:\n
    \t 1- The old password must be correct, otherwise: Error 404\n
    \t 2- Password1 and password2 must be match, otherwise: Error 401\n
    \t 3- The new password must not be the same as the old password, otherwise: Error 403\n
    \t 4- The password should not be easy, otherwise: Error 400\n
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            value = serializer.data

            if value['password1'] != value['password2']:
                return Response('Passwords must match.', status=405)
            
            try:
                validate_password(value['password1'])
            except:
                return Response('This password is too common.', status=400)
            
            if user.check_password(value['password1']):
                return Response('The new password must be different.', status=403)
            
            if not user.check_password(value['old_password']):
                return Response('The old password is wrong.', status=404)
            
            user.set_password(value['password1'])
            user.save()
            return Response('Password changed successfully.', status=200)
            
        return Response(serializer.errors, status=400)



class UserInformationView(APIView):
    """
    Get user information to store in context. These fields are returned:\n
    `id` , `username` , `profile_photo`
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserInformationSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=200)



class StoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        user = User.objects.get(username=username)
        stories = Story.objects.filter(user=user)

        if not stories:
            return Response(status=404)
        
        for story in stories:
            if not StoryViews.objects.filter(user=request.user, story=story).exists():
                all_has_seen = False
        else:
            all_has_seen = True
        
        serializer = StorySerializer(stories, context={'request': request}, many=True)
        value = {'stories': serializer.data, 'all_has_seen': all_has_seen}
        return Response(value, status=200)


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
                return Response(status=400)
            f.save()
            return Response(status=201)
        return Response(status=400)


class RemoveStoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, story_id):
        story = Story.objects.get(id=story_id)
        if request.user == story.user:
            story.delete()
            return Response(status=200)
        return Response(status=401)



class FollowView(APIView):
    """
    Receive: `user_id`\n
    If he has not followed the user, a follow will be created and if he is following, the follow will be deleted.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        auth_user = request.user
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response('User not found.', status=404)
        
        if auth_user == user:
            return Response('You can not follow yourself', status=400)
        
        follow, created = Follow.objects.get_or_create(from_user=auth_user, to_user=user)

        if not created:
            follow.delete()
            return Response('Unfollowed.', status=204)
        
        Activity.objects.get_or_create(from_user=auth_user, to_user=user, text=activity_text_follow(auth_user))
        return Response('Followed.', status=201)



class RemoveFollowerView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if Follow.objects.filter(from_user=user, to_user=request.user).exists():
            Follow.objects.get(from_user=user, to_user=request.user).delete()
            return Response(status=200)
        return Response(ststus=404)


class ListForSendPostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        following = user.following.all()
        serializer = ListForSendPostSerializer(following, many=True)
        return Response(serializer.data, status=200)



class UserSuggestionView(APIView):
    """
    A list of `suggested users` is returned.\n
    For each user, the list of users who follow him and the auth_user also follows them is displayed
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSuggestionSerializer

    def get(self, request):
        user = request.user
        following_ids = list(user.following.select_related('to_user').values_list('to_user__id', flat=True))
        following_ids.append(user.id)
        users = random.sample(list(User.objects.exclude(id__in=following_ids)), 5)

        serializer = self.serializer_class(users, context={'following_ids': following_ids}, many=True)
        return Response(serializer.data, status=200)



class UserActivities(APIView):
    """
    `User activities` are returned.
    """
    
    permission_classes = (IsAuthenticated,)
    serializer_class = UserActivitiesSerializer

    def get(self, request):
        activities = Activity.objects.select_related('from_user').filter(to_user=request.user)

        paginator = PaginateBy10()
        result_page = paginator.paginate_queryset(activities, request)
        serializer = self.serializer_class(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



class SearchUserView(APIView):
    """
    Receive: a `word`\n
    Then a `list of users` who have this word in their `username` or `name` is returned.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = SearchUserSerializer

    def get(self, request, word):
        users = User.objects.order_by('id').filter(Q(username__icontains=word) | Q(name__icontains=word))
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data, status=200)


