import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from accounts.managers import UserManager
from datetime import datetime



class User(AbstractBaseUser):
    STATUS_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('custom', 'Custom'),
        ('none', 'None'),
    )
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(max_length=150, blank=True)
    profile_photo = models.ImageField(null=True, blank=True, upload_to='user-profile')
    gender = models.CharField(max_length=17, choices=STATUS_CHOICES, default='custom')
    website = models.CharField(max_length=50, blank=True)
    private = models.BooleanField(default=False)
    open_suggestions = models.BooleanField(default=True, verbose_name='Similar account suggestions ( Include your account when recommending similar accounts people might want to follow )')
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    objects = UserManager()

    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin
    
    def has_profile_photo(self):
        if self.profile_photo:
            return True
        return False
    has_profile_photo.boolean = True
    has_profile_photo.short_description = 'PROFILE'

    def get_followers(self):
        return Follow.objects.filter(to_user=self).count()
    get_followers.short_description = 'followers'
    
    def get_followings(self):
        return Follow.objects.filter(from_user=self).count()
    get_followings.short_description = 'followings'



class Story(models.Model):
    file = models.FileField(upload_to='story')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_stories')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'stories'
    
    def extension(self):
        video_formats = ('.mp4', '.mkv', '.avi')
        image_formats = ('.jpg', '.jpeg', '.png')
        name, extension = os.path.splitext(self.file.name)
        if extension.lower() in video_formats:
            return 'video'
        elif extension.lower() in image_formats:
            return 'image'
        else:
            return 'unacceptable'

    def get_time(self):
        elapsed_time = datetime.utcnow() - self.created.replace(tzinfo=None)
        return elapsed_time
    get_time.short_description = 'elapsed time'



class StoryViews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_story_view')
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_views')

    class Meta:
        verbose_name_plural = 'story views'
    
    def get_story(self):
        return f'{self.story.user.username} - story({self.story.id})'
    get_story.short_description = 'story'



class Activity(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_activities')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    text = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'activities'
    
    def __str__(self):
        return self.text



class OtpCode(models.Model):
    email = models.CharField(max_length=255)
    code = models.CharField(max_length=10)
    created = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        elapsed_time = timezone.now() - self.created
        if elapsed_time.seconds > settings.VALID_OTP_CODE_SECONDS:
            return False
        return True
    is_valid.boolean = True
    is_valid.short_description = 'valid'

    def __str__(self):
        return self.email



from follow.models import Follow
