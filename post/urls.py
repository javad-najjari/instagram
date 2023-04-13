from django.urls import path
from . import views



app_name = 'post'
urlpatterns = [
    path('create/', views.CreatePostView.as_view()),
    # path('remove-post/<int:post_id>/', views.RemovePostView.as_view()),
    # path('detail-and-comments/<int:post_id>/', views.DetailByCommentsPostView.as_view()),
    # path('like-post/<int:post_id>/', views.LikePostView.as_view()),
    # path('like-post-double-click/<int:post_id>/', views.LikePostDoubleClickView.as_view()),
    # path('save-post/<int:post_id>/', views.SavePostView.as_view()),
    # path('create-comment/<int:post_id>/', views.CreateCommentView.as_view()),
    # # path('create-comment/<int:post_id>/<int:to_comment_id>/', views.CreateReplyCommentView.as_view()),
    # path('remove-comment/<int:comment_id>/', views.RemoveCommentView.as_view()),
    # path('post-of-followings/', views.PostOfFollowingsView.as_view()),
    # path('global/', views.PostGlobalView.as_view()),
    # path('send-post-direct/<int:post_id>/<int:user_id>/', views.SendPostView.as_view()),
    # path('search/<str:word>/', views.SearchUserView.as_view()),
]
