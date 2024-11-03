import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Lấy phòng chat
        self.room = await sync_to_async(Room.objects.get)(id=self.room_id)

        # Tham gia vào phòng chat
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Rời khỏi phòng chat
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def get_avatar_url(self):
        # Lấy URL của avatar từ profile
        return self.scope['user'].profile.avatar.url

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        user = self.scope["user"]

        # Lưu tin nhắn vào database

        if user.is_authenticated:
            message = await database_sync_to_async(Message.objects.create)(
                room=self.room,
                user=user,
                content=message_content
            )
            timestamp = message.timestamp
            # Lấy avatar URL bất đồng bộ
            avatar_url = await self.get_avatar_url()

            # Gửi tin nhắn tới các client trong phòng
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'sender': user.username,
                    'avatar_url': avatar_url,
                    'timestamp': timestamp.strftime("%b %d, %Y %I:%M %p")
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        avatar_url = event['avatar_url']
        timestamp = event['timestamp']

        # Gửi tin nhắn kèm thông tin avatar về cho client
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'avatar_url': avatar_url,  # Truyền URL avatar về client
            'timestamp': timestamp
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']  # Lấy thông tin người dùng
        self.room_group_name = 'notifications'  # Group chung cho tất cả thông báo
        self.room_group_name_user = f'user_{self.user.id}'  # Group cá nhân cho người dùng

        # Join room groups
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.room_group_name_user,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room groups
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.room_group_name_user,
            self.channel_name
        )


    # Receive message from WebSocket
    async def receive(self, text_data):
        # Xử lý các yêu cầu từ client, ví dụ: đăng ký nhận thông báo
        pass

    # Receive message from room group
    async def notification_message(self, event):
        message_data = event['notification']
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message_data))