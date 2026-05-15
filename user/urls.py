from django.contrib import admin
from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.loginUser, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('edit/', views.profile_edit, name='profile_edit'), 
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<int:user_id>/', views.chat_detail, name='chat_detail'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/api/', views.notifications_api, name='notifications_api'),
    path('messages/', views.messages_page, name='messages_page'),
]
