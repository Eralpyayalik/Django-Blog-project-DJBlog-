import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
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
        # Sadece karşı tarafa gönderiyoruz
        await self.send(text_data=json.dumps({
            'type': 'typing_status',
            'is_typing': event['is_typing'],
            'sender_id': event['sender_id']
        }))
        
    async def new_message_notification(self, event):
        # Sadece karşı tarafa gönderiyoruz
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'sender_id': event['sender_id']
        }))

