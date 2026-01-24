from channels.generic.websocket import AsyncWebsocketConsumer
from socoket_utils.group_service import GroupService
from socoket_utils.massege_serialzer import MessageSerializer
from socoket_utils.hub_handler import HubHandler

class HubConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = "hub_group"

    async def connect(self):
        self.group_service = GroupService(
            self.channel_layer, self.GROUP_NAME
        )
        self.handler = HubHandler(self.group_service)

        await self.group_service.join(self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.group_service.leave(self.channel_name)

    async def receive(self, text_data):
        payload = MessageSerializer.deserialize(text_data)
        await self.handler.handle_message(payload)

    async def hub_message(self, event):
        await self.send(
            text_data=MessageSerializer.serialize(event["message"])
        )

