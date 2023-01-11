from django.db import models
from accounts.models import User
from datetime import datetime
from post.models import Post




class Direct(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='directs')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user1} - {self.user2}'
    
    @property
    def has_messages(self):
        if self.messages:
            return True
        return False


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direct_messages')
    direct = models.ForeignKey(Direct, on_delete=models.CASCADE, related_name='messages')
    body = models.TextField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    like = models.BooleanField(default=False)
    has_seen = models.BooleanField(default=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ('-created',)
    
    def get_body(self):
        if self.body:
            return self.body[:20]
        return '-----'
    get_body.short_description = 'body'
    
    def to_user(self):
        if self.direct.user1 == self.user:
            return self.direct.user2.username
        return self.direct.user1.username

    def elapsed_time(self):
        elapsed_time = datetime.utcnow() - self.created.replace(tzinfo=None)
        return elapsed_time
    
    def get_time(self):
        return f'{self.created.hour}:{self.created.minute}'
    
    def get_post(self):
        if self.post:
            return True
        return False
    get_post.short_description = 'post'
    get_post.boolean = True

