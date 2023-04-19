from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView



app_name = 'accounts'
urlpatterns = [
    path('auth/register_email/', views.UserRegistrationEmailView.as_view()),
    path('auth/register_user/', views.UserRegistrationConfirmationView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/login/refresh/', views.CustomizeTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', views.LogoutView.as_view()),
    path('accounts/profile/<str:username>/', views.ProfileView.as_view()),
    path('accounts/posts/<str:username>/', views.UserProfilePosts.as_view()),
    path('accounts/saved_posts/', views.SavedPostsView.as_view()),
    path('accounts/edit/profile/', views.EditProfileView.as_view()),
    path('accounts/edit/profile_photo/', views.EditProfilePhotoView.as_view()),
    path('accounts/<str:username>/followers/', views.FollowersView.as_view()),
    path('accounts/<str:username>/following/', views.FollowingView.as_view()),
    path('accounts/change/password/', views.ChangePasswordView.as_view()),
    path('accounts/user_information/', views.UserInformationView.as_view()),
    path('accounts/search/<str:word>/', views.SearchUserView.as_view()),
    # path('story/<str:username>/', views.StoryView.as_view()),
    # path('story/', views.CreateStoryView.as_view()),
    # path('remove-story/<int:story_id>/', views.RemoveStoryView.as_view()),
    path('accounts/follow/<int:user_id>/', views.FollowView.as_view()),
    path('accounts/remove_follower/<int:user_id>/', views.RemoveFollowerView.as_view()),
    # path('list-for-send-post/', views.ListForSendPostView.as_view()),
    path('accounts/suggestion/', views.UserSuggestionView.as_view()),
    path('accounts/activities/', views.UserActivities.as_view()),

]

