from django.contrib import admin
from .models import Chat, Message



class MessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'related_chat', 'timestamp')


admin.site.register(Chat)
admin.site.register(Message, MessageAdmin)
