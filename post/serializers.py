from rest_framework import serializers
from .models import Post, File, Comment, PostSave, PostLike
from accounts.serializers import UserPostDetailSerializer
from datetime import datetime
from follow.models import Follow
from accounts.models import User




class CommentSerializer(serializers.ModelSerializer):
    user = UserPostDetailSerializer()
    comment_likes = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    # replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'body', 'created', 'comment_likes', 'can_delete')
    
    # def get_replies(self, obj):
    #     if obj.replies.count() != 0:
    #         replies = obj.replies.all()
    #         serializer = CommentSerializer(replies, many=True)
    #         return serializer.data
    #     else:
    #         return None
    
    def get_comment_likes(self, obj):
        return obj.comment_likes.count()
    
    def get_can_delete(self, obj):
        if self.context['auth_user'] == obj.user or self.context['auth_user'] == self.context['post_user']:
            return True
        return False


class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('body',)


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ('id', 'page', 'extension')


# TODO: متدهای این سریالایزر اصلا بهینه نیست . تعداد کوءری های خیلی زیادی به دیتابیس میزنه . باید بعدا درستشون کنم
class PostListProfileSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    has_save = serializers.SerializerMethodField()
    has_like = serializers.SerializerMethodField()
    multi_files = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'file', 'likes_count', 'comments_count', 'page_count', 'has_save', 'has_like', 'multi_files')
    
    def get_file(self, obj):
        file = obj.files.first()
        serializer = FileSerializer(file)
        return serializer.data
    
    def get_likes_count(self, obj):
        return obj.post_likes.count()
    
    def get_comments_count(self, obj):
        return obj.post_comments.count()
    
    def get_has_save(self, obj):
        return PostSave.objects.filter(user=self.context['request'].user, post=obj).exists()
    
    def get_has_like(self, obj):
        return PostLike.objects.filter(user=self.context['request'].user, post=obj).exists()
    
    def get_multi_files(self, obj):
        return obj.files.count() > 1


class PostDetailSerializer(serializers.ModelSerializer):
    user = UserPostDetailSerializer()
    auth_username = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    # comments_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    has_save = serializers.SerializerMethodField()
    has_like = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    has_own = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'user', 'auth_username', 'files', 'caption', 'created', 'likes_count',
            'comments', 'has_save', 'has_like', 'is_following', 'has_own'
        )
    
    def get_files(self, obj):
        files = obj.files.all()
        serializer = FileSerializer(files, many=True)
        return serializer.data
    
    def get_likes_count(self, obj):
        return obj.post_likes.count()
    
    def get_comments_count(self, obj):
        return obj.post_comments.count()
    
    def get_comments(self, obj):
        comments = obj.post_comments.all()
        serializer = CommentSerializer(
            comments,
            context={'auth_user': self.context['request'].user, 'post_user': obj.user},
            many=True
            )
        return serializer.data
    
    def get_has_save(self, obj):
        if PostSave.objects.filter(user=self.context['request'].user, post=obj).exists():
            return True
        return False
    
    def get_has_like(self, obj):
        if PostLike.objects.filter(user=self.context['request'].user, post=obj).exists():
            return True
        return False
    
    def get_is_following(self, obj):
        auth_user = self.context['request'].user
        if Follow.objects.filter(from_user=auth_user, to_user=obj.user).exists():
            return True
        elif auth_user == obj.user:
            return None
        return False
    
    def get_has_own(self, obj):
        auth_user = self.context['request'].user
        if auth_user == obj.user:
            return True
        return False
    
    def get_auth_username(self, obj):
        return self.context['request'].user.username


class PostWithoutCommentsSerializer(serializers.ModelSerializer):
    user = UserPostDetailSerializer()
    files = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    has_save = serializers.SerializerMethodField()
    has_like = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'user', 'files', 'caption', 'created', 'likes_count', 'comments_count', 'has_save', 'has_like')
    
    def get_files(self, obj):
        files = obj.files.all()
        serializer = FileSerializer(files, many=True)
        return serializer.data
    
    def get_likes_count(self, obj):
        return obj.post_likes.count()
    
    def get_comments_count(self, obj):
        return obj.post_comments.count()
    
    def get_has_save(self, obj):
        if PostSave.objects.filter(user=self.context['request'].user, post=obj).exists():
            return True
        return False
    
    def get_has_like(self, obj):
        if PostLike.objects.filter(user=self.context['request'].user, post=obj).exists():
            return True
        return False
    
    def get_created(self, obj):
        elapsed_time = datetime.utcnow() - obj.created.replace(tzinfo=None)
        t = int(elapsed_time.total_seconds())
        if t < 60:
            return f'{t} seconds'
        elif t < 3600:
            if t // 60 == 1:
                return '1 minute'
            return f'{t//60} minutes'
        elif t < 86400:
            if t // 3600 == 1:
                return '1 hour'
            return f'{t // 3600} hours'
        elif t < 604800:
            if t // 86400 == 1:
                return '1 day'
            return f'{t // 86400} days'
        elif t // 604800 == 1:
            return '1 week'
        return f'{t // 604800} weeks'


class PostListGlobalSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    multi_files = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'file', 'multi_files', 'likes_count', 'comments_count')
    
    def get_file(self, obj):
        file = obj.files.first()
        serializer = FileSerializer(file)
        return serializer.data
    
    def get_multi_files(self, obj):
        if obj.files.count() > 1:
            return True
        return False
    
    def get_has_save(self, obj):
        if PostSave.objects.filter(user=self.context['request'].user, post=obj).exists():
            return True
        return False
    
    def get_has_like(self, obj):
        if PostLike.objects.filter(user=self.context['request'].user, post=obj).exists():
            return True
        return False
    
    def get_likes_count(self, obj):
        return obj.post_likes.count()
    
    def get_comments_count(self, obj):
        return obj.post_comments.count()
    

class PostSendDirectSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('user', 'file')
    
    def get_file(self, obj):
        file = obj.files.first()
        serializer = FileSerializer(file)
        return serializer.data


class SearchUserSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('name', 'username', 'profile_photo')
    
    def get_profile_photo(self, obj):
        photo = obj.profile_photo
        if photo:
            return photo.url
        return None

