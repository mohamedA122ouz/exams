"""
ASGI config for exams project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from web_socket.MiddleWare import WebSocketLoginRequiredMiddleware
from web_socket.Router import MainRouter
from channels.security.websocket import AllowedHostsOriginValidator
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exams.settings')

application = ProtocolTypeRouter({
    "http":get_asgi_application(),
    # "websocket": AllowedHostsOriginValidator( #needed in the Production
    #     AuthMiddlewareStack(
    #         WebSocketLoginRequiredMiddleware( 
    #             URLRouter([
    #                 path("ws/", MainRouter.as_asgi()) #type:ignore
    #             ])
    #         )
    #     )
    # )
    "websocket": #For Testing purpose
    AuthMiddlewareStack(
        WebSocketLoginRequiredMiddleware( 
            URLRouter([
                path("ws/", MainRouter.as_asgi()) #type:ignore
            ])
        )
    )
})
