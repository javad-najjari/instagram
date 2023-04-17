from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .forms import UserCreationForm, UserChangeForm
from .models import User, Story, StoryViews, Activity, OtpCode



class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'email', 'get_followers', 'get_followings', 'has_profile_photo',
                    'is_active', 'is_admin'
                )
    list_filter = ('is_active',)
    fieldsets = (
        ('Information', {'fields': (
            'username', 'email', 'name', 'website', 'gender',
            'open_suggestions', 'private', 'profile_photo', 'bio'
            )}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'last_login', 'password')}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'email', 'password1', 'password2')}),
    )

    search_fields = ('username', 'email')
    ordering = ('-is_admin', 'id')
    filter_horizontal = ()


class StoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_time', 'extension')

class StoryViewsAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_story')

class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'is_valid')


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(Story, StoryAdmin)
admin.site.register(StoryViews, StoryViewsAdmin)
admin.site.register(Activity)
admin.site.register(OtpCode, OtpCodeAdmin)
