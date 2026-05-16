from web_socket.Handlers.Chat.types.messageStatus import seenStatus
from web_socket.Handlers.Chat.types.messages import channelEvent, sendMessage_S, sentMessage_D
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
class ReceiverHandler:
    async def receive_message(self:"AsyncJsonWebsocketConsumer",event:channelEvent[sentMessage_D]):#type:ignore
        messageSerializer = sendMessage_S(data=event["message"])
        isMessage = await sync_to_async(messageSerializer.is_valid)()
        if isMessage:
            currentData:sentMessage_D = messageSerializer.data #type:ignore
            currentData["status"] = seenStatus.DELIVERED.value
            currentData["status_text"] = seenStatus.DELIVERED.name
            await self.send_json({"type": "receive_message", "message": currentData})
        #------------------
    #------------------