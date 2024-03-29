import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .serializers import MessageSerializer
from rest_framework.renderers import JSONRenderer
from .models import Message, Chat
from django.contrib.auth import get_user_model


User = get_user_model()



class ChatConsumer(WebsocketConsumer):

    def new_message(self, data):
        message = data['message']
        author = data['username']
        chat_model = Chat.objects.get(id=data['chat_id'])
        user_model = User.objects.filter(username=author).first()
        if message != '':
            message_model = Message.objects.create(author=user_model, content=message, related_chat=chat_model)
            result = eval(self.message_serializer(message_model))
            self.send_to_chat_message(result)

    def fetch_message(self, data):
        chat_id = data['chat_id']
        messages = Message.objects.filter(related_chat__id=chat_id).order_by('timestamp')
        messages_json = self.message_serializer(messages)
        content = {
            'message': eval(messages_json),
            'command': 'fetch_message',
        }
        self.send(text_data=json.dumps(content))
    
    # def image(self, data):
    #     self.send_to_chat_message(data)
    
    
    def message_serializer(self, qs):
        is_many = True if qs.__class__.__name__ == 'QuerySet' else False
        serializer = MessageSerializer(qs, many=is_many)
        content = JSONRenderer().render(serializer.data)
        return content

    
    def connect(self):
        self.chat = self.scope['url_route']['kwargs']['chat']
        self.chat_group_name = f'chat_{self.chat}'

        async_to_sync(self.channel_layer.group_add)(
            self.chat_group_name,
            self.channel_name
        )
        self.accept()

    
    commands = {
        'new_message': new_message,
        'fetch_message': fetch_message,
        # 'img': image,
    }

    
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_dict = json.loads(text_data)
        command = text_data_dict['command']

        self.commands[command](self, text_data_dict)

    def send_to_chat_message(self, message):

        command = message.get('command', None)

        async_to_sync(self.channel_layer.group_send)(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'content': message['content'],
                'command': (lambda command: 'img' if (command=='img') else 'new_message')(command),
                '__str__': message['__str__']
            }
        )
    
