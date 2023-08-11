from django.db import models
from django.contrib.auth import get_user_model



User = get_user_model()



class Chat(models.Model):
    members = models.ManyToManyField(User, blank=True)

    def __str__(self):
        members = self.members.all()
        result = ' - '.join(m.username for m in members)
        # return self.members.first().username
        return result



class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    related_chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def last_messages(self, room_name):
        return Message.objects.filter(related_chat__room_name=room_name).order_by('-timestamp')
    
    def __str__(self):
        return f'{self.author.username}  ->  {self.content}'

