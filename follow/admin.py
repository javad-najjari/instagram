from django.contrib import admin
from .models import Follow




class FollowAdmin(admin.ModelAdmin):
    ordering = ('id',)

admin.site.register(Follow, FollowAdmin)
