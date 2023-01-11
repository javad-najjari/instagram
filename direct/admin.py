from django.contrib import admin
from .models import Direct, Message



class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'to_user', 'get_body', 'get_post', 'has_seen', 'elapsed_time')


admin.site.register(Direct)
admin.site.register(Message, MessageAdmin)
