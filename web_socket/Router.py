
import json
from typing import Any, cast
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from core.services.types.userType import IUserHelper
from core.services.utils.generalOutputHelper import GOutput
from web_socket.Handlers.Chat.types.messages import messageWrapper_D, messageWrapper_S, sentMessage_D
from web_socket.Handlers.importer import IMPORTER
from web_socket.types.exams import MessageEvent



class MainRouter(AsyncJsonWebsocketConsumer,IMPORTER):
    ConnectCommitteCommand = "Please Join Committee"
    async def connect(self) -> None:
        user = self.scope.get("user")
        if user and user.is_authenticated:
            print(user.get_username())
            await self.accept()
            await self.send_json(GOutput({"success":f"welcome {user.get_username()}"}))
            user = cast(IUserHelper,user)
        #---------------
        else:
            await self.accept()
            await self.send_json(GOutput(
                error={"unauthorized":"cannot access this resource"}
            ))
            await self.close(code=4003)
    #---------------
    async def receive_json(self, content: MessageEvent, **kwargs: Any) -> None:
        print("I am at least inside")
        data_s = messageWrapper_S(data=content)
        if data_s.is_valid():
            validData:messageWrapper_D = data_s.validated_data
            wantedHandlerName = validData["endpoint"]
            wantedHandler = getattr(self,wantedHandlerName,None)
            if wantedHandler is not None and callable(wantedHandler):
                await wantedHandler(validData["message"]) #type:ignore
            #------------------
            else:
                await self.send_json(GOutput(error={"endpoint":"is not found"}))
                await self.close(code=4004) 
            await self.send("thank you for your cooperation")
        else:
            await self.send(str(data_s.errors))
    async def test1(self,content:sentMessage_D):
        print(content)
    #------------------