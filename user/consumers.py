import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from user.models import Profile

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def update_user_last_seen(self):
        if self.user and self.user.is_authenticated:
            Profile.objects.filter(user=self.user).update(last_seen=timezone.now())

    async def connect(self):
        try:
            self.user = self.scope.get('user')
            
            if self.user and self.user.is_authenticated:
                self.user_group_name = f'user_{self.user.id}'
                
                await self.channel_layer.group_add(
                    self.user_group_name,
                    self.channel_name
                )
                
                await self.accept()
                # Bağlandığında çevrim içi bilgisini güncelle
                await self.update_user_last_seen()
                logger.info(f"WebSocket connected: User {self.user.id}")
            else:
                logger.warning("WebSocket connection rejected: User not authenticated")
                await self.close()
        except Exception as e:
            logger.error(f"WebSocket connect error: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            if hasattr(self, 'user_group_name'):
                await self.channel_layer.group_discard(
                    self.user_group_name,
                    self.channel_name
                )
        except Exception as e:
            logger.error(f"WebSocket disconnect error: {str(e)}")

    async def receive(self, text_data):
        try:
            # Her aktivitede çevrim içi bilgisini güncelle
            await self.update_user_last_seen()
            
            data = json.loads(text_data)
            msg_type = data.get('type')
            
            if msg_type == 'typing_status':
                receiver_id = data.get('receiver_id')
                if receiver_id:
                    receiver_group = f'user_{receiver_id}'
                    await self.channel_layer.group_send(
                        receiver_group,
                        {
                            'type': 'typing_status_message',
                            'is_typing': data.get('is_typing', False),
                            'sender_id': self.user.id
                        }
                    )
        except Exception as e:
            logger.error(f"WebSocket receive error: {str(e)}")

    async def typing_status_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing_status',
            'is_typing': event['is_typing'],
            'sender_id': event['sender_id']
        }))
        
    async def new_message_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'sender_id': event['sender_id']
        }))

    async def new_notification(self, event):
        # Beğeni, Yorum Beğenisi vb. genel bildirimler için
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'sender_id': event.get('sender_id'),
            'notification_type': event.get('notification_type'),
            'text': event.get('text')
        }))

