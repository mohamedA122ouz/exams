class GroupService:
    def __init__(self, channel_layer, group_name: str):
        self.channel_layer = channel_layer
        self.group_name = group_name

    async def join(self, channel_name: str):
        await self.channel_layer.group_add(self.group_name, channel_name)

    async def leave(self, channel_name: str):
        await self.channel_layer.group_discard(self.group_name, channel_name)

    async def broadcast(self, message: str):
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "hub.message",
                "message": message,
            },
        )

