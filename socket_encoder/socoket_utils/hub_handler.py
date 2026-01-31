from channels.auth import UserLazyObject
from django.contrib.auth.models import User
from core.models.Exams_models import messages,classRoom
from socket_encoder.socoket_utils.group_service import GroupService
from channels.db import database_sync_to_async
from core.services.classRoomService import classRoomService

class HubHandler:
    def __init__(self, group_service: GroupService):
        self.group_service = group_service

    #-----------------------------------------------
    async def handle_join(self, channel_name: str):
        await self.group_service.join(channel_name)
    #-----------------------------------------------
    async def handle_leave(self, channel_name: str):
        await self.group_service.leave(channel_name)
    #-----------------------------------------------


    # see if the user is authenticated or not
    async def handle_user_auth(self,scope:dict)->bool:
        user = scope["user"]
        if not user or not user.is_authenticated:
            return False
        # check if the user is authorized or can acces the class room
        if not await self.__is_authorized(scope):
            return False
        return True
    #-----------------------------------------------

    async def __is_authorized(self,scope:dict)->bool:
       # create clas room based on current user scope
       user= scope["user"]
       class_room_service=classRoomService(user)
       goup_name= self.group_service.group_name

       class_room=await self.get_class_room_instance(self.group_service.group_name)

       # check if the user is authorized or can acces the class room
       @database_sync_to_async
       def check_class_privelges():
        auth_resource= class_room_service.accessClassRoom(class_room)
        if not auth_resource["isSuccess"]:
            return False
        return True

       return await check_class_privelges()
    #-----------------------------------------------
    async def save_message(self, message: str|None,sender:UserLazyObject|None)->None:

        # save the message into db or redis
        group_name = self.group_service.group_name
        class_room=await self.get_class_room_instance(group_name)
        if not class_room:
            return
        
        @database_sync_to_async
        def _save():
            messages.objects.create(Owner=sender,text=message,classRoom=class_room)
        
        await _save()
        
    async def get_class_room_instance(self,class_room_id:str)->classRoom:
        @database_sync_to_async
        def _get():
            try:
                return classRoom.objects.get(ID=int(class_room_id.split("_")[1]))
            except classRoom.DoesNotExist:
                return None
        
        return await _get()
    async def handle_message(self, payload: dict|None,sender:UserLazyObject|None)->None:
        if not payload:
            return

        message = payload.get("message")
        if not message:
            return
        await self.save_message(message,sender)
        
        # braodcast the message

        await self.group_service.channel_layer.group_send(
            self.group_service.group_name,
            {
                "type": "hub.message",
                "message": message,
                "sender": sender,
            }
        )
        
