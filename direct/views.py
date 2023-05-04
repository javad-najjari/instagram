import json
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from .models import Chat, Message
from .serializers import ChatSerializer, ChatDetailSerializer, MessageSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated



User = get_user_model()





class DirectList(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatSerializer

    def get(self, request):
        user = request.user
        chat_rooms = Chat.objects.filter(members=user)
        serializer = self.serializer_class(chat_rooms, context={'user_id': user.id}, many=True)
        return Response(serializer.data, status=200)



class Direct(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatDetailSerializer

    def get(self, request, username):
        obj_user = User.objects.get(username=username)
        auth_user = request.user

        chat = Chat.objects.filter(members=obj_user).filter(members=auth_user).first()
        if not chat:
            return Response('Chat not found.', status=404)
        
        serializer = self.serializer_class(chat, context={'obj_user': obj_user})
        return Response(serializer.data, status=200)




# class CreateChat(APIView):
#     permission_classes = (IsAuthenticated,)

#     def get(self, request, username):
#         auth_user = request.user
#         obj_user = User.objects.filter(username=username).first()
#         if not obj_user:
#             return Response('User not found', status=401)

#         chat = Chat.objects.filter(members=auth_user).filter(members=obj_user).first()
#         if not chat:
#             chat = Chat.objects.create()
#             chat.members.add(auth_user)
#             chat.members.add(obj_user)
        
#         context = {
#             'chat': chat,
#             'user': obj_user
#         }
#         # context = {
#         #     'room_name': room_name,
#         #     'username': mark_safe(json.dumps(request.user.username)),
#         # }
#         serializer = ChatDetailSerializer(chat, context={'user_id': auth_user.id})
#         return Response(serializer.data, status=200)

