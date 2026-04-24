
from core.models.Exams_models import ProfileSettings
from channels.db import database_sync_to_async,aclose_old_connections
from channels.auth import login,logout
from channels.generic.websocket import AsyncWebsocketConsumer
from web_socket.Handlers.importer import IMPORTER



class MainRouter(AsyncWebsocketConsumer,IMPORTER):
    
    async def connect(self) -> None:
        user = self.scope.get("user")
        cookies = self.scope.get("cookies")
        headers = self.scope.get("headers")
        print(cookies)
        print(headers)
        if user and user.is_authenticated:
            await login(self.scope,user) #type:ignore
            print(user.get_username())
            await self.accept()
            await self.send("Welcome "+user.get_username())
            await self.channel_layer.send(channel=self.channel_name,message={
                "type":"recieveMessage",
                "text":"test"
            })
            await self.send(self.channel_name)
            # user.Settings.socketID = self.channel_name
            # database_sync_to_async(lambda: ProfileSettings.objects.filter())
        #---------------
        else:
            await self.accept()
            await self.send("unauthorized Access")
            await self.close(code=4003)
    #---------------