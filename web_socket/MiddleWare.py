from channels.db import database_sync_to_async

class WebSocketLoginRequiredMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        user = scope.get("user")
        
        # Check if authenticated
        if not user or not user.is_authenticated:
            # You can send a close message or just ignore
            await send({
                "type": "websocket.close",
                "code": 4003, # Custom close code
            })
            return
        return await self.inner(scope, receive, send)
    #---------------
#---------------