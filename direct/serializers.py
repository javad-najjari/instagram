from rest_framework import serializers
from accounts.serializers import UserInformationSerializer
from .models import Message, Chat



class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('__str__', 'author', 'content', 'timestamp')



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

    class Meta:
        model = Chat
        fields = ('id', 'user',)
    
    def get_user(self, obj):
        obj_user = obj.members.exclude(id=self.context['user_id']).first()
        serializer = UserInformationSerializer(obj_user)
        return serializer.data


