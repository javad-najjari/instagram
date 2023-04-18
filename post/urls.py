from django.urls import path
from . import views



app_name = 'post'
urlpatterns = [
    path('create/', views.CreatePostView.as_view()),
    path('delete/<int:post_id>/', views.RemovePostView.as_view()),
    path('detail/<int:post_id>/', views.PostDetailView.as_view()),
    path('home/', views.HomeView.as_view()),
    path('like/<int:post_id>/', views.LikePostView.as_view()),
    path('like_double_click/<int:post_id>/', views.LikePostDoubleClickView.as_view()),
    path('save/<int:post_id>/', views.SavePostView.as_view()),
    path('comment/create/<int:post_id>/', views.CreateCommentView.as_view()),
    path('comment/delete/<int:comment_id>/', views.RemoveCommentView.as_view()),
    path('explore/', views.ExploreView.as_view()),
    # path('send-post-direct/<int:post_id>/<int:user_id>/', views.SendPostView.as_view()),
]
