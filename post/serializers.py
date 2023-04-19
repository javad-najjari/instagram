from rest_framework import serializers
from .models import Post, File, Comment, PostSave, PostLike
from accounts.serializers import UserPostDetailSerializer
from datetime import datetime
from follow.models import Follow
from utils import elapsed_time




class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ('id', 'page', 'extension')



class CreatePostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    files = serializers.FileField()

    class Meta:
        model = Post
        fields = ('user', 'caption', 'files')

    def get_user(self, obj):
        return self.context.get('user')



class CommentSerializer(serializers.ModelSerializer):
    user = UserPostDetailSerializer()
    can_delete = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'body', 'created', 'can_delete')

    def get_can_delete(self, obj):
        if self.context['auth_user'] == obj.user or self.context['auth_user'] == self.context['post_user']:
            return True
        return False

    def get_created(self, obj):
        e_time = datetime.utcnow() - obj.created.replace(tzinfo=None)
        return elapsed_time(e_time.total_seconds())



class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('body',)



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
    comments = serializers.SerializerMethodField()
    has_save = serializers.SerializerMethodField()
    has_like = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'user', 'auth_username', 'files', 'caption', 'created', 'likes_count',
            'comments', 'has_save', 'has_like', 'is_following', 'is_owner'
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
        comments = obj.post_comments.all().order_by('-created')
        serializer = CommentSerializer(
            comments, context={'auth_user': self.context['request'].user, 'post_user': obj.user}, many=True
            )
        return serializer.data

    def get_has_save(self, obj):
        return PostSave.objects.filter(user=self.context['request'].user, post=obj).exists()

    def get_has_like(self, obj):
        return PostLike.objects.filter(user=self.context['request'].user, post=obj).exists()

    def get_is_following(self, obj):
        auth_user = self.context['request'].user
        return Follow.objects.filter(from_user=auth_user, to_user=obj.user).exists()

    def get_is_owner(self, obj):
        auth_user = self.context['request'].user
        if auth_user == obj.user:
            return True
        return False

    def get_auth_username(self, obj):
        return self.context['request'].user.username



class PostWithoutCommentsSerializer(serializers.ModelSerializer):
    user = UserPostDetailSerializer()
    files = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='post_likes.count')
    comments_count = serializers.IntegerField(source='post_comments.count')
    has_save = serializers.SerializerMethodField()
    has_like = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'user', 'files', 'caption', 'created', 'likes_count', 'comments_count', 'has_save', 'has_like'
        )

    def get_files(self, obj):
        files = obj.files.all()
        serializer = FileSerializer(files, many=True)
        return serializer.data

    def get_has_save(self, obj):
        return PostSave.objects.filter(user=self.context['request'].user, post=obj).exists()

    def get_has_like(self, obj):
        return PostLike.objects.filter(user=self.context['request'].user, post=obj).exists()

    def get_created(self, obj):
        e_time = datetime.utcnow() - obj.created.replace(tzinfo=None)
        t = int(e_time.total_seconds())
        return elapsed_time(t)



class PostExploreSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    multi_files = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='post_likes.count')
    comments_count = serializers.IntegerField(source='post_comments.count')

    class Meta:
        model = Post
        fields = ('id', 'file', 'multi_files', 'likes_count', 'comments_count')

    def get_file(self, obj):
        file = obj.files.first()
        serializer = FileSerializer(file)
        return serializer.data

    def get_multi_files(self, obj):
        return obj.files.count() > 1



class PostSendDirectSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('user', 'file')

    def get_file(self, obj):
        file = obj.files.first()
        serializer = FileSerializer(file)
        return serializer.data

