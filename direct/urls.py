from django.urls import path
from . import views



urlpatterns = [
    path('', views.Direct.as_view()),
    path('<str:username>/', views.CreateChat.as_view(), name='room'),
]
