from socket_encoder.socoket_utils.group_service import GroupService
class HubHandler:
    def __init__(self, group_service: GroupService):
        self.group_service = group_service

    async def handle_message(self, payload: dict|None):
        if not payload:
            return

        message = payload.get("message")
        if not message:
            return

        await self.group_service.broadcast(message)
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
        
