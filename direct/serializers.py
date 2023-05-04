from rest_framework import serializers
from accounts.serializers import UserInformationSerializer
from .models import Message, Chat



class MessageSerializer(serializers.ModelSerializer):
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('is_author', 'content')
    
    def get_is_author(self, obj):
        return obj.author != self.context.get('obj_user')



class ChatSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ('user',)
    
    def get_user(self, obj):
        obj_user = obj.members.exclude(id=self.context.get('user_id')).first()
        serializer = UserInformationSerializer(obj_user)
        return serializer.data



class ChatDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ('user', 'messages')
    
    def get_user(self, obj):
        obj_user = self.context.get('obj_user')
        serializer = UserInformationSerializer(obj_user)
        return serializer.data
    
    def get_messages(self, obj):
        messages = Message.objects.filter(related_chat=obj)
        serializer = MessageSerializer(messages, context={'obj_user': self.context.get('obj_user')}, many=True)
        return serializer.data

