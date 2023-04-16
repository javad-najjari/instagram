from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import (
    PostDetailSerializer, CommentCreateSerializer, PostWithoutCommentsSerializer, PostExploreSerializer,
    SearchUserSerializer, CreatePostSerializer
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Post, File, Comment, PostLike, PostSave
from .paginations import PaginateBy5, PaginateBy15
from follow.models import Follow
from direct.models import Message, Direct
from accounts.models import User, Activities
from django.db import connection, reset_queries
from django.db.models import Q, Count




class CreatePostView(APIView):
    """
    Receive: `caption` , `files`\n
    Note: The number of received files must be between 1 and 10, otherwise: `Error 401`\n
    Note: The extension of the received files must be currect, otherwise: `Error 400`\n
    \t for pictures:  `jpg` , `jpeg` , `png`\n
    \t for videos :  `mp4` , `mkv` , `avi` , `mkv`\n
    And then the post will be created with status code `201`
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = CreatePostSerializer

    def post(self, request):
        caption = request.data.get('caption')
        files = request.FILES.getlist('files')
        files_count = len(files)

        if not (0 < files_count < 11):
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



class PostDetailView(APIView):
    """
    Receive: `post_id`\n
    Get: `post details`
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = PostDetailSerializer

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response('Post not found.', status=404)
        
        serializer = self.serializer_class(post, context={'request': request})
        return Response(serializer.data, status=200)



# TODO: این ویو میتونه خیلی بهتر و بهینه تر بشه . باید روش کار بشه
class HomeView(APIView):
    """
    A list of `following posts` is returned.
    """
    
    permission_classes = (IsAuthenticated,)
    serializer_class = PostWithoutCommentsSerializer

    def get(self, request):
        user = request.user
        following_ids = user.following.select_related('to_user').values_list('to_user__id', flat=True)
        posts = Post.objects.prefetch_related(
            'files', 'post_likes', 'post_comments', 'post_saves'
        ).filter(user__id__in=following_ids).order_by('-created')

        paginator = PaginateBy5()
        result_page = paginator.paginate_queryset(posts, request)
        serializer = self.serializer_class(result_page, context={'request': request}, many=True)
        return paginator.get_paginated_response(serializer.data)



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



class RemoveCommentView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user or request.user == comment.post.user:
            comment.delete()
            return Response(status=200)
        return Response(status=401)



class ExploreView(APIView):
    """
    A list of `posts` is returned.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = PostExploreSerializer

    def get(self, request):
        user = request.user
        following_ids = list(user.following.select_related('to_user').values_list('to_user__id', flat=True))
        following_ids.append(user.id)
        posts = Post.objects.exclude(user__id__in=following_ids).annotate(
            num_likes=Count('post_likes')
            ).order_by('-num_likes')
        
        paginator = PaginateBy15()
        result_page = paginator.paginate_queryset(posts, request)
        serializer = self.serializer_class(result_page, context={'request': request}, many=True)
        return paginator.get_paginated_response(serializer.data, )



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

