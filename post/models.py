import os
from datetime import datetime
from django.db import models
from accounts.models import User




class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')
    caption = models.TextField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        if self.caption:
            return f'{self.user} - {self.caption[:30]} ...'
        return f'{self.user} - NO CAPTION ...'
    
    def page_count(self):
        return self.files.count()
    
    def short_caption(self):
        if self.caption:
            return f'{self.caption[:50]} ...'
        return 'NO CAPTION'
    short_caption.short_description = 'caption'

    def get_time(self):
        elapsed_time = datetime.utcnow() - self.created.replace(tzinfo=None)
        return elapsed_time
    get_time.short_description = 'elapsed time'

    def get_views(self):
        return self.post_views.count()
    get_views.short_description = 'views'



class File(models.Model):
    page = models.FileField(upload_to='post')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='files')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)
    
    def extension(self):
        video_formats = ('.mp4', '.mkv', '.avi', '.mkv')
        image_formats = ('.jpg', '.jpeg', '.png')
        name, extension = os.path.splitext(self.page.name)
        if extension.lower() in video_formats:
            return 'video'
        elif extension.lower() in image_formats:
            return 'image'
        else:
            return 'unacceptable'

    def get_post(self):
        return f'{self.post.id} - {self.post.user}'
    get_post.short_description = 'post'



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments', verbose_name='to post')
    body = models.TextField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.user} - {self.body[:30]} ...'

    def short_body(self):
        return self.body[:30] + ' ...'
    short_body.short_description = 'message text'



class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')

    def __str__(self):
        if self.post.caption:
            return f'{self.user} - ({self.post.user}) {self.post.caption[:30]} ...'
        return f'{self.user} - ({self.post.user}) NO CAPTION ...'



class PostSave(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_saves')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_saves')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.post.caption:
            return f'{self.user} - ({self.post.user}) {self.post.caption[:30]} ...'
        return f'{self.user} - ({self.post.user}) NO CAPTION ...'



class PostViews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_views')

    class Meta:
        verbose_name_plural = 'Post views'

