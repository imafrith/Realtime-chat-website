from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [
  path('',index,name="home"),
  path('profile',profile,name="profile"),
    path('profile-update',ProfileUpdateView.as_view(), name='profile-update'),
  path('login',signin,name="login"),
    path('register',register,name="register"),


  path('chats',chat_view,name="chats"),

  path('group',group,name="group"),
  path('groupname/<slug:name>/',chat_view,name="chatgroup"),

  path('contact',contact,name="contact"),
 path('chat/<username>/', get_or_create_chatroom, name="start-chat"),
  path('chat/room/<chatroom_name>', chat_view_private, name="chatroom"),
  path('chatsdisplay',chatsdisplay,name="chatsdisplay"),
  path('logout',logoutuser,name="logout-user"),

]