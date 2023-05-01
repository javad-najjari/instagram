from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import (
    PostDetailSerializer, CommentCreateSerializer, PostWithoutCommentsSerializer, PostExploreSerializer,
    CreatePostSerializer
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Post, File, Comment, PostLike, PostSave
from paginations import PaginateBy5, PaginateBy15
from direct.models import Message
from accounts.models import User, Activity
from django.db import connection, reset_queries
from django.db.models import Q, Count
from utils import is_user_allowed, activity_text_like




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
        post = Post.objects.filter(id=post_id).first()
        if not post:
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

    """
    Receive: `post_id`\n
    If he has not liked the post, a like will be created and if he has liked, the like will be deleted.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, post_id):
        auth_user = request.user
        post = Post.objects.select_related('user').filter(id=post_id).first()
        if not post:
            return Response('Post not found.', status=404)
        
        user = post.user
        like, created = PostLike.objects.get_or_create(user=auth_user, post=post)

        if not created:
            like.delete()
            return Response('Unliked.', status=204)
        
        Activity.objects.get_or_create(from_user=auth_user, to_user=user, text=activity_text_like(auth_user))
        return Response('Liked.', status=201)



class LikePostDoubleClickView(APIView):
    """
    Receive: `post_id`\n
    If he has not liked the post, a like will be created.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, post_id):
        auth_user = request.user
        post = Post.objects.select_related('user').filter(id=post_id).first()
        if not post:
            return Response('Post not found.', status=404)
        
        user = post.user
        _ , created = PostLike.objects.get_or_create(user=auth_user, post=post)

        if not created:
            Activity.objects.get_or_create(from_user=auth_user, to_user=user, text=activity_text_like(auth_user))
        
        return Response('Liked.', status=201)



class SavePostView(APIView):
    """
    Receive: `post_id`\n
    If the post has not been saved, it will be saved, and if it has not been saved, it will be saved.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, post_id):
        user = request.user
        post = Post.objects.select_related('user').filter(id=post_id).first()
        post_save = PostSave.objects.filter(user=user, post=post).first()

        if not post:
            return Response('Post not found.', status=404)
        
        if not is_user_allowed(user, post.user):
            return Response('You are not allowed to save this post.', status=401)
        
        if not post_save:
            PostSave.objects.create(user=user, post=post)
            return Response('Post saved.', status=200)
        
        post_save.delete()
        return Response('Post unsaved.', status=200)



class CreateCommentView(APIView):
    """
    Receive: `post_id` in url and the `body` key in body\n
    Then if the user `is allowed` to comment on this post, the `comment` will be created
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = CommentCreateSerializer

    def post(self, request, post_id):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        post = Post.objects.select_related('user').filter(id=post_id).first()

        if not post:
            return Response('Post not found.', status=404)

        if not is_user_allowed(user, post.user):
            return Response('You are not allowed to comment on this post.', status=401)
        
        if serializer.is_valid():
            Comment.objects.create(user=user, body=serializer.validated_data['body'], post=post)
            return Response('Comment created.', status=201)
        return Response(serializer.errors, status=400)



class RemoveCommentView(APIView):
    """
    Receive: comment_id\n
    Then, if the `auth_uesr = the user who created the comment` or the `auth_user = the user who created the post`,
    the comment will be deleted.
    """

    permission_classes = (IsAuthenticated,)

    def delete(self, request, comment_id):
        user = request.user
        comment = Comment.objects.select_related('user', 'post__user').filter(id=comment_id).first()
        if not comment:
            return Response('Comment not found.', status=404)

        if (user == comment.user) or (user == comment.post.user):
            comment.delete()
            return Response('Comment deleted.', status=204)
        return Response('You are not allowed to delete this comment.', status=401)



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
        serializer = self.serializer_class(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



# class SendPostView(APIView):
#     def post(self, request, post_id, user_id):
#         auth_user = request.user
#         to_user = get_object_or_404(User, id=user_id)
#         post = get_object_or_404(Post, id=post_id)
#         direct = Direct.objects.get(Q(user1=auth_user, user2=to_user) | Q(user1=to_user, user2=auth_user))
#         Message.objects.create(user=auth_user, direct=direct, post=post)
#         return Response(status=201)

