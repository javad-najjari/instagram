from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from rest_framework import routers



app_name = 'accounts'
urlpatterns = [
    path('register/', views.UserRegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.ProfileView.as_view()),
    path('profile/<str:username>/', views.ProfileView.as_view()),
    path('saved/', views.ProfileAndSavedView.as_view()),
    path('<str:username>/followers/', views.FollowersView.as_view()),
    path('<str:username>/following/', views.FollowingView.as_view()),
    path('accounts/edit/', views.EditProfileView.as_view()),
    path('accounts/edit-profile-photo/', views.EditProfilephotoView.as_view()),
    # path('accounts/edit-profile-photo/', views.EditProfilephotoViewSet.as_view()),
    path('accounts/password/change/', views.ChangePasswordView.as_view()),
    path('story/<str:username>/', views.StoryView.as_view()),
    path('story/', views.CreateStoryView.as_view()),
    path('remove-story/<int:story_id>/', views.RemoveStoryView.as_view()),
    path('follow/<int:user_id>/', views.FollowView.as_view()),
    path('unfollow/<int:user_id>/', views.UnFollowView.as_view()),
    path('remove-follower/<int:user_id>/', views.RemoveFollowerView.as_view()),
    path('list-for-send-post/', views.ListForSendPostView.as_view()),
    path('suggestion/', views.UserSuggestionView.as_view()),
    path('activities/', views.UserActivities.as_view()),

]

# router = routers.SimpleRouter()
# router.register('user', views.EditProfilephotoViewSet, basename='User')
# urlpatterns += router.urls
