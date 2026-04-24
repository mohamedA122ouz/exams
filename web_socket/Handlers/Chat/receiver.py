
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from channels.generic.websocket import AsyncWebsocketConsumer


class Receiver:
    
    async def recieveMessage(self:"AsyncWebsocketConsumer",event):
        await self.send("okay I am working")