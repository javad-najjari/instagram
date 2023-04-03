from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User, Story, StoryViews, Activities
from follow.models import Follow
from utils import validate_profile_photo_size




class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {
                'validators': [UniqueValidator(queryset=User.objects.all())],
                'error_messages': {'unique': 'username already exists.'}
            },
            'email': {'validators': [UniqueValidator(queryset=User.objects.all())]},
        }
    
    def create(self, validated_data):
        del validated_data['password2']
        return User.objects.create_user(**validated_data)
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('passwords must be match !!!')
        return data



class GetCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)



class ProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    full_access_to_profile = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'name', 'followers_count', 'following_count', 'profile_photo', 'bio',
            'full_access_to_profile', 'is_following'
        )
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    
    def get_full_access_to_profile(self, obj):
        return self.context.get('full_access_to_profile')
    
    def get_profile_photo(self, obj):
        photo = obj.profile_photo
        if photo:
            return photo.url
    
    def get_is_following(self, obj):
        auth_user = self.context.get('request').user
        if Follow.objects.filter(from_user=auth_user, to_user=obj).exists():
            return True
        elif auth_user == obj:
            return None
        return False



class EditProfileSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(read_only=True)
    username = serializers.CharField(required=False, read_only=True)
    email = serializers.EmailField(required=False, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'profile_photo', 'name', 'username', 'website', 'bio', 'email', 'gender','open_suggestions')



class EditProfilePhotoSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(validators=[validate_profile_photo_size])
    
    class Meta:
        model = User
        fields = ('profile_photo',)



class ListOfFollowersSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='from_user.username')
    name = serializers.CharField(source='from_user.name')
    user_id = serializers.IntegerField(source='from_user.id')
    profile_photo = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'username', 'name', 'profile_photo', 'is_following', 'user_id')
    
    def get_profile_photo(self, obj):
        photo = obj.from_user.profile_photo
        if photo:
            return photo.url
    
    def get_is_following(self, obj):
        user = obj.to_user
        if Follow.objects.filter(from_user=self.context['request'].user, to_user=user).exists():
            return True
        elif self.context['request'].user == user:
            return None
        return False



class ListOfFollowingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='to_user.username')
    name = serializers.CharField(source='to_user.name')
    user_id = serializers.IntegerField(source='to_user.id')
    profile_photo = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'username', 'name', 'profile_photo', 'is_following', 'user_id')
    
    def get_profile_photo(self, obj):
        photo = obj.to_user.profile_photo
        if photo:
            return photo.url
    
    def get_is_following(self, obj):
        user = obj.to_user
        if Follow.objects.filter(from_user=self.context['request'].user, to_user=user).exists():
            return True
        elif self.context['request'].user == user:
            return None
        return False



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()



class UserPostDetailSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('profile_photo', 'name', 'username')
    
    def get_profile_photo(self, obj):
        photo = obj.profile_photo
        if photo:
            return photo.url
        return None



class StorySerializer(serializers.ModelSerializer):
    user = UserPostDetailSerializer()
    views = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    has_seen = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ('id', 'user', 'file', 'created', 'views', 'views_count', 'extension', 'has_seen')
    
    def get_views(self, obj):
        auth_user = self.context['request'].user
        if auth_user == obj.user:
            users = obj.story_views.all()
            final_users = []
            for user in users:
                final_users.append(user.user)
            serializer = UserPostDetailSerializer(final_users, many=True)
            return serializer.data
        return False
    
    def get_views_count(self, obj):
        auth_user = self.context['request'].user
        if auth_user == obj.user:
            return obj.story_views.count()
        return False
    
    def get_has_seen(self, obj):
        auth_user = self.context['request'].user
        if StoryViews.objects.filter(user=auth_user, story=obj).exists():
            return True
        return False



class UserSearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('profile_photo', 'username', 'name')


class ListForSendPostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('username', 'profile_photo', 'user_id')
    
    def get_username(self, obj):
        return obj.to_user.username
    
    def get_profile_photo(self, obj):
        photo = obj.to_user.profile_photo
        if photo:
            return photo.url
        return None
    
    def get_user_id(self, obj):
        return obj.to_user.id


class UserListSuggestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username',)


class UserSuggestionSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()
    followed_by = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'profile_photo', 'followed_by')
    
    def get_profile_photo(self, obj):
        photo = obj.profile_photo
        if photo:
            return photo.url
        return None

    def get_followed_by(self, obj):
        auth_user = self.context['request'].user
        users = []
        for follower in obj.followers.all():
            # if follower in auth_user.following.all():
            if Follow.objects.filter(from_user=auth_user, to_user=follower.from_user).exists():
                users.append(follower.from_user)
        serializer = UserListSuggestionSerializer(users, many=True)
        return serializer.data


class UserActivity(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'profile_photo')


class UserActivitiesSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Activities
        fields = ('user', 'follow', 'like')
    
    def get_user_photo(self, obj):
        user = obj.from_user
        photo = user.profile_photo
        if photo:
            return photo.url
        return None
    
    def get_username(self, obj):
        return obj.from_user.username
    
    def get_user(self, obj):
        user = obj.from_user
        user = UserActivity(user)
        return user.data

