from channels.generic.websocket import AsyncWebsocketConsumer
from core.models.Exams_models import ProfileSettings
from channels.db import database_sync_to_async,aclose_old_connections
from channels.auth import login,logout
# Get Rid of Zombie socket names or ID
ProfileSettings.objects.filter(socketID__isnull=False).update(socketID=None)
#---------------FINISHED-SETUP#---------------



class MainRouter(AsyncWebsocketConsumer):
    
    
    async def connect(self) -> None:
        user = self.scope.get("user")
        cookies = self.scope.get("cookies")
        headers = self.scope.get("headers")
        print(cookies)
        print(headers)
        if user and user.is_authenticated:
            await login(self.scope,user) #type:ignore
            print(user.get_username())
            # database_sync_to_async(lambda: ProfileSettings.objects.filter())
            await self.accept()
            await self.send("it is connected")
            await self.send(user.get_username())
        #---------------
        else:
            await self.accept()
            await self.send("unauthorized Access")
            await self.close(code=4003)
    #---------------