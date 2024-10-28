from django.urls import path,re_path
from .consumers import *

websocket_urlpatterns = [
    path("ws/chatroom/<chatroom_name>",ChatroomConsumer.as_asgi()),
      re_path(r'ws/chats/$', ChatConsumer.as_asgi()),

 
      
]   