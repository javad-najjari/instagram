from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    UserRegistrationSerializer, ProfileSerializer, ListOfFollowersSerializer, ListOfFollowingSerializer,
    EditProfileSerializer, ChangePasswordSerializer, StorySerializer, EditProfilephotoSerializer,
    ListForSendPostSerializer, UserSuggestionSerializer, UserActivitiesSerializer
)
from post.serializers import PostListSerializer
from rest_framework import status
from .models import StoryViews, User, Story, Activities
from rest_framework.permissions import IsAuthenticated
from follow.models import Follow




class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        value = serializer.data
        
        if User.objects.filter(username=value['username']).exists():
            context = {'message': 'username already exists'}
            return Response(context, status=status.HTTP_409_CONFLICT)

        if User.objects.filter(email=value['email']).exists():
            context = {'message': 'email already exists'}
            return Response(context, status=status.HTTP_409_CONFLICT)
        
        if User.objects.filter(phone_number=value['phone_number']).exists():
            context = {'message': 'phone number already exists'}
            return Response(context, status=status.HTTP_409_CONFLICT)
        
        if value['password'] != value['password2']:
            context = {'message': 'passwords must be match'}
            return Response(context, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username=None):
        if username:
            user = get_object_or_404(User, username=username)
        else:
            user = request.user
        
        is_following = Follow.objects.filter(from_user=request.user, to_user=user).exists()
        user_allowed_see_profile_full = request.user == user or is_following or not user.private
        profile_serializer = ProfileSerializer(user, context={'is_allowed': user_allowed_see_profile_full, 'request': request})
        context = {'profile': profile_serializer.data}
        if user_allowed_see_profile_full:
            posts = user.user_posts.all()
            posts_serializer = PostListSerializer(posts, context={'request': request}, many=True)
            context['posts'] = posts_serializer.data
        return Response(context, status=status.HTTP_200_OK)


class ProfileAndSavedView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if request.user == user:
            posts = user.user_saves.all()
            new_posts = [post.post for post in posts]
            profile_serializer = ProfileSerializer(user, context={'is_allowed': True, 'request': request})
            posts_serializer = PostListSerializer(new_posts, context={'request': request}, many=True)
            data = {'profile': profile_serializer.data, 'saved': posts_serializer.data}
            return Response(data)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class FollowersView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        user = User.objects.get(username=username)
        is_following = Follow.objects.filter(from_user=request.user, to_user=user).exists()
        user_allowed = request.user == user or is_following or not user.private
        if user_allowed:
            followers = user.followers.all()
            serializer = ListOfFollowersSerializer(followers, context={'request': request}, many=True)
            return Response(serializer.data)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class FollowingView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        user = User.objects.get(username=username)
        is_following = Follow.objects.filter(from_user=request.user, to_user=user).exists()
        user_allowed = request.user == user or is_following or not user.private
        if user_allowed:
            following = user.following.all()
            serializer = ListOfFollowingSerializer(following, context={'request': request}, many=True)
            return Response(serializer.data)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class EditProfileView(APIView):
    def get(self, request):
        user = request.user
        serializer = EditProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = request.user
        serializer = EditProfileSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditProfilephotoView(APIView):
    def put(self, request):
        user = request.user
        serializer = EditProfilephotoSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user = request.user
        user.profile_photo.delete()
        user.save()
        return Response(status=status.HTTP_200_OK)


# class EditProfilephotoViewSet(viewsets.ModelViewSet):
#     serializer_class = EditProfilephotoSerializer
#     # parser_classes = (MultiPartParser, FormParser)
#     permission_classes = (IsAuthenticated,)
#     queryset = User.objects.all()

#     def get_queryset(self):
#         return self.queryset.filter(user=self.request.user)

#     @action(methods=['POST'], detail=True, url_path='upload-image')
#     def upload_image(self, request, pk=None):
#         user = User.objects.get(id=pk)
#         if user != request.user:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
#         serializer = EditProfilephotoSerializer(instance=user, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(status=status.HTTP_200_OK)
#         return Response(status=status.HTTP_400_BAD_REQUEST)

 
#     # def put(self, request):
#     #     user = request.user
#     #     serializer = EditProfilephotoSerializer(instance=user, data=request.data)
#     #     if serializer.is_valid():
#     #         serializer.save()
#     #         return Response(serializer.data, status=status.HTTP_200_OK)
#     #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     # def delete(self, request):
#     #     user = request.user
#     #     user.profile_photo.delete()
#     #     user.save()
#     #     return Response(status=status.HTTP_200_OK)


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
        followings = user.following.all()
        serializer = ListForSendPostSerializer(followings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSuggestionView(APIView):
    def get(self, request):
        user = request.user
        followings = user.following.all()
        users = []
        for following in followings:
            for end_user in following.to_user.following.all():
                if not Follow.objects.filter(from_user=user, to_user=end_user.to_user).exists() and end_user.to_user != user:
                    users.append(end_user.to_user)
        final_users = sorted(users, key=lambda x:users.count(x), reverse=True)
        for item in final_users:
            if final_users.count(item) > 1:
                final_users.remove(item)
        if len(final_users) > 4:
            final_users = final_users[:5]
        
        serializer = UserSuggestionSerializer(final_users, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserActivities(APIView):
    def get(self, request):
        activity = Activities.objects.filter(to_user=request.user)
        serializer = UserActivitiesSerializer(activity, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

