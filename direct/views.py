from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import User
from .models import Direct, Message
from django.db.models import Q
from .serializers import AllDirectSerializer, DirectDetailSerializer, CreateMessageSerializer
from accounts.serializers import UserSearchSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from direct.models import Direct, Message




class AllDirectView(APIView):
    def get(self, request):
        user = request.user
        directs = list(Direct.objects.filter(Q(user1=user) | Q(user2=user)))
        for direct in enumerate(directs):
            if not direct[1].messages.all():
                directs.pop(direct[0])
        directs.sort(key=lambda x:x.messages.first().created, reverse=True) # why first() ? because of class Meta in Message model
        serializer = AllDirectSerializer(directs, context={'request': request}, many=True)
        if directs:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class DirectDetailView(APIView):
    def get(self, request, username):
        user = User.objects.get(username=username)
        try:
            direct = Direct.objects.get(Q(user1=request.user, user2=user) | Q(user1=user, user2=request.user))
            messages = direct.messages.all().order_by('created')
            serializer = DirectDetailSerializer(messages, context={'request': request}, many=True)
            if messages:
                last_message = messages.last()
                if request.user != last_message.user:
                    last_message.has_seen = True
                    last_message.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)
        except Direct.DoesNotExist:
            direct = Direct.objects.create(user1=request.user, user2=user)
            messages = direct.messages.all().order_by('created')
            serializer = DirectDetailSerializer(messages, context={'request': request}, many=True)
            return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)


class LikeDirectMessageView(APIView):
    def post(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        if message.user != request.user:
            if not message.like:
                message.like = True
            else:
                message.like = False
            message.save()
            return Response(status=status.HTTP_200_OK)


class RemoveDirectMessageView(APIView):
    def post(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        if message.user == request.user:
            message.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class DirectSearchView(APIView):
    def get(self, request, search):
        user = request.user
        following = user.following.all()
        result_users = []
        for user in following:
            if search in user.to_user.username or search in user.to_user.name:
                result_users.append(user.to_user)
        
        if len(result_users) < 10:
            extra_users = User.objects.filter(Q(username__contains=search) | Q(name__contains=search))
        for user in extra_users:
            if user not in result_users:
                result_users.append(user)
                if len(result_users) == 10:
                    break
        
        serializer = UserSearchSerializer(result_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateMessageView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, direct_id):
        serializer = CreateMessageSerializer(data=request.data)
        user = request.user
        direct = get_object_or_404(Direct, id=direct_id)
        if serializer.is_valid():
            Message.objects.create(
                user=user, direct=direct, body=serializer.validated_data['body']
            )
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

