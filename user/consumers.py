import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            # Her kullanıcıyı kendi ID'sine özel bir gruba ekliyoruz
            self.user_group_name = f'user_{self.user.id}'
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')
        
        # Typing status sinyalini alıp sadece ilgili alıcıya iletiyoruz
        if msg_type == 'typing_status':
            receiver_id = data.get('receiver_id')
            if receiver_id:
                receiver_group = f'user_{receiver_id}'
                await self.channel_layer.group_send(
                    receiver_group,
                    {
                        'type': 'typing_status_message',
                        'is_typing': data.get('is_typing'),
                        'sender_id': self.user.id
                    }
                )

    # Yazıyor bilgisini frontend'e basan event
    async def typing_status_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing_status',
            'is_typing': event['is_typing'],
            'sender_id': event['sender_id']
        }))
        
    # Yeni mesaj bildirimini (views.py'dan tetiklenen) frontend'e basan event
    async def new_message_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'sender_id': event['sender_id']
        }))
