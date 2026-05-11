from web_socket.Handlers.Chat.types.messages import channelEvent, sendMessage_S, sentMessage_D
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
class ReceiverHandler:
    async def receive_message(self:"AsyncJsonWebsocketConsumer",event:channelEvent[sentMessage_D]):#type:ignore
        messageSerializer = sendMessage_S(data=event["message"])
        isMessage = await sync_to_async(messageSerializer.is_valid)()
        if isMessage:
            await self.send_json(messageSerializer.validated_data)
        #------------------
    #------------------