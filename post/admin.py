from django.contrib import admin
from .models import File, Post, Comment, PostLike, PostSave, PostViews



class FileAdmin(admin.ModelAdmin):
    list_display = ('get_post', 'extension')


class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_caption', 'get_views', 'get_time', 'page_count')
    ordering = ('id',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'short_body')



class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')


class PostSaveAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created')


class PostViewsAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')


admin.site.register(File, FileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(PostSave, PostSaveAdmin)
admin.site.register(PostViews, PostViewsAdmin)
