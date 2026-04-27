
import json
from typing import Any, cast
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from core.services.types.userType import IUserHelper
from core.services.utils.generalOutputHelper import GOutput
from web_socket.Handlers.importer import IMPORTER
from web_socket.types.exams import MessageEvent



class MainRouter(AsyncJsonWebsocketConsumer,IMPORTER):
    ConnectCommitteCommand = "Please Join Committee"
    async def connect(self) -> None:
        user = self.scope.get("user")
        cookies = self.scope.get("cookies")
        headers = self.scope.get("headers")
        print(cookies)
        print(headers)
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
        if content["RequestType"] == "Committee" and not content["TriggerPoint"] and content["Description"] == self.ConnectCommitteCommand:
            user = self.scope.get("user")
            self.Committee_Connect(user)

