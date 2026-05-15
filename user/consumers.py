import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.room_group_name = f'user_{self.user.id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'typing':
            receiver_id = data.get('receiver_id')
            if receiver_id:
                receiver_group = f'user_{receiver_id}'
                await self.channel_layer.group_send(
                    receiver_group,
                    {
                        'type': 'chat_typing',
                        'sender_id': self.user.id
                    }
                )

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'sender_id': event['sender_id']
        }))
        
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'sender_id': event['sender_id']
        }))
