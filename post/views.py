from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import (
    PostDetailSerializer, CommentCreateSerializer, PostWithoutCommentsSerializer, PostListGlobalSerializer,
    SearchUserSerializer, CreatePostSerializer
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Post, File, Comment, PostLike, PostSave, PostViews
from .paginations import HomePagination, GlobalPagination
from follow.models import Follow
from direct.models import Message, Direct
from accounts.models import User, Activities
from django.db import connection, reset_queries
from django.db.models import Q




class CreatePostView(APIView):
    """
    Receive: `caption` , `files`\n
    Note: The number of received files must be between 1 and 10, otherwise: `Error 401`\n
    Note: The extension of the received files must be currect, otherwise: `Error 400`\n
    \t for pictures:  `jpg` , `jpeg` , `png`\n
    \t for videos :  `mp4` , `mkv` , `avi`\n
    And then the post will be created with status code `201`
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = CreatePostSerializer

    def post(self, request):
        caption = request.data.get('caption')
        files = request.FILES.getlist('files')
        files_count = len(files)

        if not (0 < files_count < 10):
            return Response(f'Number of files should be between 1 and 10. Received {files_count} files.', status=401)
        
        for file in files:
            if File(page=file).extension() == 'unacceptable':
                return Response('File extension is not acceptable.', status=400)
        
        post = Post.objects.create(user=request.user, caption=caption)
        File.objects.bulk_create([File(page=file, post=post) for file in files])

        return Response('Post created.', status=201)



class RemovePostView(APIView):
    """
    Receive: `post_id`\n
    If `auth_user` = `post_user`  =>  The post will be deleted.
    """

    permission_classes = (IsAuthenticated,)

    def delete(self, request, post_id):
        post = Post.objects.select_related('user').filter(id=post_id).first()
        if not post:
            return Response('Post not found.', status=404)
        
        if request.user == post.user:
            post.delete()
            return Response('Post deleted.', status=200)
        
        return Response('You are not the owner.', status=401)



class LikePostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, id=post_id)
        if PostLike.objects.filter(user=user, post=post).exists():
            if Activities.objects.filter(from_user=user, to_user=post.user, post_id=post.id, like=True).exists():
                Activities.objects.get(from_user=user, to_user=post.user, post_id=post.id, like=True).delete()
            PostLike.objects.get(user=user, post=post).delete()
            return Response(status=200)
        if user != post.user:
            Activities.objects.create(
                from_user=user, to_user=post.user, post_id=post.id, like=True
            )
        PostLike.objects.create(user=user, post=post)
        return Response(status=200)


class LikePostDoubleClickView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, id=post_id)
        if not PostLike.objects.filter(user=user, post=post).exists():
            if user != post.user:
                if not Activities.objects.filter(from_user=user, to_user=post.user, post_id=post.id, like=True).exists():
                    Activities.objects.create(
                        from_user=user, to_user=post.user, post_id=post.id, like=True
                    )
            PostLike.objects.create(user=user, post=post)
            return Response(status=200)
        return Response(status=100)


class SavePostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, id=post_id)
        if not PostSave.objects.filter(user=user, post=post).exists():
            PostSave.objects.create(user=user, post=post)
            return Response(status=200)
        PostSave.objects.get(user=user, post=post).delete()
        return Response(status=200)


class CreateCommentView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, post_id):
        serializer = CommentCreateSerializer(data=request.data)
        post = get_object_or_404(Post, id=post_id)
        if serializer.is_valid():
            Comment.objects.create(
                user = request.user, body = serializer.validated_data['body'],
                post = post
            )
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# class CreateReplyCommentView(APIView):
#     permission_classes = (IsAuthenticated,)

#     def post(self, request, post_id, to_comment_id):
#         serializer = CommentCreateSerializer(data=request.data)
#         post = Post.objects.get(id=post_id)
#         to_comment = Comment.objects.get(id=to_comment_id)
#         if serializer.is_valid():
#             Comment.objects.create(
#                 user = request.user, body = serializer.validated_data['body'],
#                 post = post, to_comment = to_comment, is_reply = True
#             )
#             return Response(serializer.data, status=HTTP_201_CREATED)
#         return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class RemoveCommentView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user or request.user == comment.post.user:
            comment.delete()
            return Response(status=200)
        return Response(status=401)


class DetailByCommentsPostView(APIView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostDetailSerializer(post, context={'request': request})
        if not PostViews.objects.filter(post=post, user=request.user).exists():
            PostViews.objects.create(post=post, user=request.user)
        return Response(serializer.data, status=200)


class PostOfFollowingsView(generics.ListAPIView):

    queryset = Post.objects
    pagination_class = HomePagination

    def get(self, request):
        user = request.user
        following_posts = [follow.to_user.user_posts.all() for follow in user.following.all()]
        posts = []
        for post in following_posts:
            for p in post:
                posts.append(p)
        
        posts.sort(key= lambda x:x.created, reverse=True)
        serializer = PostWithoutCommentsSerializer(posts, context={'request': request}, many=True)
        results = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(results)


class PostGlobalView(generics.ListAPIView):

    queryset = Post.objects
    pagination_class = GlobalPagination

    def get(self, request):
        auth_user = request.user
        posts = Post.objects.all()
        final_posts = []
        for post in posts:
            follow = Follow.objects.filter(from_user=auth_user, to_user=post.user).exists()
            if not follow and post.user != auth_user:
                final_posts.append(post)
        
        final_posts.sort(key = lambda x: x.post_likes.count(), reverse=True)
        serializer = PostListGlobalSerializer(final_posts, context={'request': request}, many=True)
        results = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(results)


class SendPostView(APIView):
    def post(self, request, post_id, user_id):
        auth_user = request.user
        to_user = get_object_or_404(User, id=user_id)
        post = get_object_or_404(Post, id=post_id)
        direct = Direct.objects.get(Q(user1=auth_user, user2=to_user) | Q(user1=to_user, user2=auth_user))
        Message.objects.create(user=auth_user, direct=direct, post=post)
        return Response(status=201)


class SearchUserView(APIView):
    def get(self, request, word):
        users = User.objects.all()
        result_users = []
        for user in users:
            if (word in user.username or word in user.name) and user != request.user:
                result_users.append(user)
        serializer = SearchUserSerializer(result_users, many=True)
        return Response(serializer.data, status=200)

