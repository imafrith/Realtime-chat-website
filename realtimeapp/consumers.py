from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
import json
from .models import *
from django.core.exceptions import ObjectDoesNotExist

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async 
from django.core.serializers.json import DjangoJSONEncoder
import logging
from django.forms.models import model_to_dict
import asyncio

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name'] 
        self.chatroom = get_object_or_404(Chatgroup, group_name=self.chatroom_name)
        
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )
                # Add the user to the online users list of the chat group
        self.chatroom.users_online.add(self.user)
        GroupMessage.objects.filter(group=self.chatroom, is_read=False).exclude(author=self.user).update(is_read=True)
        self.accept()


        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )
        # remove and update online users
  
        
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']
        
        message = GroupMessage.objects.create(
            body = body,
            author = self.user, 
            group = self.chatroom 
        )
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )
        
    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        if self.user in self.chatroom.users_online.all():
                GroupMessage.objects.filter(group=self.chatroom, is_read=False).exclude(author=self.user).update(is_read=True)
        
        context = {
            'message': message,
            'user': self.user,
            'chat_group': self.chatroom
        }
        
        html = render_to_string("partials/chat_message_p.html", context=context)
        self.send(text_data=html)
 




class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        self.groups = await self.get_user_private_chat_groups()
        
        # Join room/group channels
        for group in self.groups:
            await self.channel_layer.group_add(
                f"chat_{group.id}",
                self.channel_name
            )
        
        await self.accept()
        await self.send_latest_chats({})  # Send initial latest chats
        print(f"WebSocket connection established for user: {self.user}")

        # Start periodic task to send latest chats every 10 seconds
        await self.start_sending_latest_chats()

    async def disconnect(self, close_code):
        for group in self.groups:
            await self.channel_layer.group_discard(
                f"chat_{group.id}",
                self.channel_name
            )
        print(f"WebSocket connection closed for user: {self.user}")

        # Stop periodic task if the connection is closed
        await self.stop_sending_latest_chats()

    async def receive(self, text_data):
        # Handle incoming WebSocket messages (if any)
        print(f"Message received: {text_data}")

    async def send_latest_chats(self, event):
        latest_chats = await self.fetch_latest_chats()

        latest_chats_serializable = []
        for chat in latest_chats:
            profile_photo_url = await self.get_profile_photo_url(chat['receiver'])

            group_name = await self.get_group_name(chat['message'])

            latest_chats_serializable.append({
                'receiver': chat['receiver'].username,
                'profile_photo': profile_photo_url,
                'message': {
                    'content': chat['message'].body,
                    'created': chat['message'].created.isoformat(),
                    'group_name': group_name if group_name else None,
                  
                },
                'new_message_count': chat['new_message_count']
            })

        await self.send(text_data=json.dumps({
            'latest_chat': latest_chats_serializable
        }))

    @database_sync_to_async
    def get_user_private_chat_groups(self):
        return list(Chatgroup.objects.filter(member=self.user, is_private=True))



    @sync_to_async 
    def fetch_latest_chats(self):
        # Fetch the latest chats for the user asynchronously
        chatsroom = Chatgroup.objects.filter(member=self.user, is_private=True)
        
        # Dictionary to hold the latest chat for each user and new message count
        latest_chats = {}

        for chat in chatsroom:
            # Fetching all unique members of this chat group except the current user
            members = chat.member.exclude(pk=self.user.pk)
            
            for member in members:
                try:
                    # Try to get the latest message from this member
                    latest_message = GroupMessage.objects.filter(group=chat, author=member).latest('created')
                    # Count unread messages for this member in the chat group
                    unread_count = GroupMessage.objects.filter(group=chat, author=member, is_read=False).count()
                except ObjectDoesNotExist:
                    # Handle the case where no messages exist (unlikely if chat exists)
                    latest_message = None
                    unread_count = 0

                # Store in dictionary if it's the latest message
                if latest_message:
                    if member not in latest_chats or latest_message.created > latest_chats[member]['message'].created:
                        latest_chats[member] = {'message': latest_message, 'count': unread_count}

        # Convert the dictionary to a list of messages for the template
        latest_chats_list = []
        for member, data in latest_chats.items():
            latest_chats_list.append({
                'receiver': member,
                'message': data['message'],
                'new_message_count': data['count']
            })
        
        # Sort the list based on the most recent message
        latest_chats_list.sort(key=lambda x: x['message'].created, reverse=True)
        
        return latest_chats_list  # Return the list of latest chats

    @database_sync_to_async
    def get_profile_photo_url(self, receiver):
        try:
            profile = Profile.objects.get(user=receiver)
            if profile.profile_image:
                return profile.profile_image.url
            return None
        except ObjectDoesNotExist:
            return None
        

    @database_sync_to_async
    def get_group_name(self, message):
        try:
            group_name = message.group.group_name
            return group_name
        except ObjectDoesNotExist:
            return None

    async def start_sending_latest_chats(self):
        self.sending_latest_chats = True
        while self.sending_latest_chats:
            await self.send_latest_chats({})
            await asyncio.sleep(1)  # Send updates every seconds

    async def stop_sending_latest_chats(self):
        self.sending_latest_chats = False