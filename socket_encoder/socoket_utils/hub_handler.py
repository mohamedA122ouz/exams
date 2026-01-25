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
    async def handle_message(self, payload: dict|None)->None:
        if not payload:
            return

        message = payload.get("message")
        user = payload.get("user")
        if not message:
            return
        # braodcast the message

        await self.group_service.channel_layer.group_send(
            self.group_service.group_name,
            {
                "type": "hub.message",
                "message": message,
                "sender": user  
            }
        )
        
