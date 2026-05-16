
from typing import TYPE_CHECKING

from core.services.types.userType import IUserHelper
from core.services.utils.generalOutputHelper import GOutput
from web_socket.Handlers.Chat.types.messages import ContentWrapper_D, sendMessage_S, sentMessage_D
from web_socket.Handlers.utils.registerHandler import AddHandler
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

if TYPE_CHECKING:
    from channels.generic.websocket import AsyncJsonWebsocketConsumer


class SenderHandler:
    @AddHandler
    async def sendTo(self:"AsyncJsonWebsocketConsumer",ContentWrapper:ContentWrapper_D[sentMessage_D]):#type:ignore
        usr:IUserHelper = self.scope.get("user")#type:ignore
        allowedGroups = usr.chatRooms
        messageSerializer = sendMessage_S(data=ContentWrapper["message"])
        isMessageValid = await sync_to_async(messageSerializer.is_valid)()
        if not isMessageValid:
            await self.send_json(GOutput(error={"failed":"message formate is wrong or invalid"}))
        # message:sentMessage_D = messageSerializer.validated_data
        for group in ContentWrapper["sendTo_groupID"]:
            if not await database_sync_to_async(allowedGroups.contains)(group):
                continue
            #------------------
            await self.channel_layer.group_send(
                str(group.id),#type:ignore
                {
                    "type":"receive_message",
                    "message":ContentWrapper["message"]
                }
            )
        #------------------
    #------------------
    @AddHandler
    async def connectMe(self:"AsyncJsonWebsocketConsumer",event:dict):#type:ignore
        usr:IUserHelper = self.scope.get("user")#type:ignore
        allowedGroups = await database_sync_to_async(list)(usr.chatRooms.all().values("id"))
        for group in allowedGroups:
            await self.channel_layer.group_add(
                str(group["id"]),#type:ignore
                self.channel_name
            )
        #------------------
    #------------------
#------------------