
import inspect
from typing import Any, cast
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from core.services.types.userType import IUserHelper
from core.services.utils.generalOutputHelper import GOutput
from web_socket.Handlers.Chat.types.messages import ContentWrapper_D, ContentWrapper_S, sentMessage_D
from web_socket.Handlers.importer import IMPORTER
from web_socket.Handlers.utils.registerHandler import SecureHandler
from asgiref.sync import sync_to_async


@SecureHandler
class MainRouter(AsyncJsonWebsocketConsumer,IMPORTER):
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
    async def receive_json(self, content: Any, **kwargs: Any) -> None:
        data_s = ContentWrapper_S(data=content)
        if await sync_to_async(data_s.is_valid)():
            validData:ContentWrapper_D = data_s.validated_data
            if hasattr(self,"_allowedHandlers"):
                allowedHandlers = getattr(self,"_allowedHandlers")
                if validData["endpoint"] in allowedHandlers and callable(allowedHandlers[validData["endpoint"]]): #type:ignore
                    wantedHandler = self._allowedHandlers[validData["endpoint"]]#type:ignore
                    if inspect.iscoroutinefunction(wantedHandler):
                        await wantedHandler(self,validData)
                    #------------------
                    else:
                        wantedHandler(self,validData)
                    #------------------
                #------------------
                else:
                    await self.send("sorry cannot access this method 404, thank you for your cooperation")
                    await self.close()
                    return
                #------------------
            else:
                await self.send("sorry cannot access this method 404, thank you for your cooperation")
                await self.close()
                return
            #------------------ 
        else:
            await self.send(str(data_s.errors))
        #------------------
    #------------------
#------------------