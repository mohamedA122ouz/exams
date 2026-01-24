from channels.generic.websocket import AsyncWebsocketConsumer
from socket_encoder.socoket_utils.group_service import GroupService
from socket_encoder.socoket_utils.massege_serialzer import MessageSerializer
from socket_encoder.socoket_utils.hub_handler import HubHandler
from socket_encoder.socoket_utils.json_handler.request_sch import ClassRoomConnectSerializer


# class room hub consumer

class HubConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Validate classroom_id using schema
        serializer = ClassRoomConnectSerializer(data=self.scope["url_route"]["kwargs"])
        if not serializer.is_valid():
            await self.close()
            return

        self.classroom_id = serializer.validated_data["classroom_id"]
        self.group_name = f"classroom_{self.classroom_id}"

        # assign each class to a diffrent session 
        self.group_service = GroupService(
            self.channel_layer, self.group_name
        )

        # activate the socket handler
        self.handler = HubHandler(self.group_service)

        if not await self.handler.handle_user_auth(self.scope):
            await self.send(
                text_data=MessageSerializer.serialize("You are not authenticated")
            )
            await self.close()

            return

        await self.handler.handle_join(self.channel_name)
        await self.accept()

        await self.send(
            text_data=MessageSerializer.serialize(f"{user.get_username()} has joined the classroom")
        )

    async def disconnect(self, close_code):
        await self.group_service.leave(self.channel_name)

    async def receive(self, text_data):
        payload = MessageSerializer.deserialize(text_data)
        await self.handler.handle_message(payload)

    async def hub_message(self, event):
        await self.send(
            text_data=MessageSerializer.serialize(event["message"])
        )

