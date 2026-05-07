
from typing import TYPE_CHECKING

from web_socket.Handlers.Chat.types.messages import messageWrapper_D, sendMessage_S


if TYPE_CHECKING:
    from channels.generic.websocket import AsyncWebsocketConsumer


class SenderHandler:
    
    async def messageHandler(self:"AsyncWebsocketConsumer",event:messageWrapper_D):#type:ignore
        print(event)