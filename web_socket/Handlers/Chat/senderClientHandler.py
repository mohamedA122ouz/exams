
from typing import TYPE_CHECKING

from core.services.types.userType import IUserHelper
from web_socket.Handlers.Chat.types.messages import ContentWrapper_D, sendMessage_S
from web_socket.Handlers.utils.registerHandler import AddHandler


if TYPE_CHECKING:
    from channels.generic.websocket import AsyncWebsocketConsumer


class SenderHandler:

    async def sendTo(self:"AsyncWebsocketConsumer",message:ContentWrapper_D):#type:ignore
        usr:IUserHelper = self.scope.get("user")#type:ignore
        allowedGroups = usr.chatRooms
        for group in message["sendTo_groupID"]:
            if not allowedGroups.contains(group):
                continue
            #------------------
            await self.channel_layer.group_send(
                str(group.id),#type:ignore
                {
                    "type":"send_message",
                    "message":message
                }
            )
        #------------------
    @AddHandler
    async def sendTo(self:"AsyncWebsocketConsumer",message:ContentWrapper_D):#type:ignore
        ...
    #------------------