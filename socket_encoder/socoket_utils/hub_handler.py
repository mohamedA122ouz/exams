from socket_encoder.socoket_utils.group_service import GroupService
class HubHandler:
    def __init__(self, group_service: GroupService):
        self.group_service = group_service

    async def handle_message(self, payload: dict):
        message = payload.get("message")
        if not message:
            return

        await self.group_service.broadcast(message)

