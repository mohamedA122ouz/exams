from channels.auth import UserLazyObject
from django.contrib.auth.models import User
from core.models.Exams_models import messages,classRoom
from socket_encoder.socoket_utils.group_service import GroupService
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
        return True
    async def save_message(self, message: str|None,sender:UserLazyObject|None)->None:

        # save the message into db or redis
        group_name = self.group_service.group_name
        class_room=await self.get_class_room_instance(group_name)
        print(class_room)
        if not class_room:
            return
        messages.objects.create(Owner=sender,text=message,classRoom=class_room)
    async def get_class_room_instance(self,class_room_id:str)->classRoom|None:
        class_room=classRoom.objects.get(id=class_room_id)
        if class_room:
            return class_room
        return None
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
        
