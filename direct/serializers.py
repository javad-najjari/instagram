from rest_framework import serializers
from .models import Direct, Message
from accounts.serializers import UserPostDetailSerializer
from post.serializers import PostSendDirectSerializer




class AllDirectSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    i_had_seen = serializers.SerializerMethodField()
    
    class Meta:
        model = Direct
        fields = ('user', 'last_message', 'i_had_seen')
    
    def get_user(self, obj):
        user = self.context['request'].user
        if user != obj.user1:
            to_user = obj.user1
        else:
            to_user = obj.user2
        serializer = UserPostDetailSerializer(to_user)
        return serializer.data
    
    def get_last_message(self, obj):
        message = obj.messages.first()  # why first ?   because of (class Meta) in Message model !!!
        if message.user == self.context['request'].user:
            if message.has_seen:
                return f'Seen {message.elapsed_time()}'
            else:
                return f'Sent {message.elapsed_time()} ago'
        return f'{message.body[:20]} .. - {message.elapsed_time()}'
    
    def get_i_had_seen(self, obj):
        message = obj.messages.first()
        if message.user != self.context['request'].user:
            if message.has_seen:
                return True
        return False


class DirectDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    is_auth_user = serializers.SerializerMethodField()
    post = PostSendDirectSerializer()

    class Meta:
        model = Message
        fields = ('user', 'is_auth_user', 'body', 'get_time', 'post')
    
    def get_is_auth_user(self, obj):
        if obj.user == self.context['request'].user:
            return True
        return False
    
    def get_user(self, obj):
        photo = obj.user.profile_photo
        if photo:
            return photo.url
        return None


class CreateMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('body',)

