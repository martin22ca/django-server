from channels.generic.websocket import AsyncWebsocketConsumer
import json


class TableUpdateConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connections = {}

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        user_id = self.scope['user'].id if self.scope['user'].is_authenticated else None
        if user_id in self.connections:
            del self.connections[user_id]

    async def receive(self, text_data):
        # Receive message from WebSocket
        data = json.loads(text_data)
        print('data', data)
        # Process the received data as needed
        # Perform necessary actions (e.g., update database)

        # Send message to room group
        await self.send(text_data=json.dumps({
            'message': 'Update processed successfully',
            # Add any additional data to send back to client if needed
        }))

    async def table_update(self, event):
        user_id = event['user_id']
        if user_id in self.connections:
            channel_name = self.connections[user_id]
            await self.send(text_data=json.dumps({
                'table': event['table'],
                'action': event['action'],
                'record_id': event['record_id'],
            }), channel_name=channel_name)
