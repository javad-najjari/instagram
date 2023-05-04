from django.urls import path
from . import views



urlpatterns = [
    path('', views.DirectList.as_view()),
    path('<str:username>/', views.Direct.as_view(), name='room'),
]
