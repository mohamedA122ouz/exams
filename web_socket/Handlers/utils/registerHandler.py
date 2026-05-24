from typing import Callable, Type, TypeVar
from channels.generic.websocket import AsyncWebsocketConsumer 

def AddHandler(handlerFunc:Callable):
    setattr(handlerFunc,"_allowedMethod",True)
    return handlerFunc
#------------------
T = TypeVar("T", bound=AsyncWebsocketConsumer)
def SecureHandler(cls:Type[T])->Type[T]:
    cls._allowedHandlers = {} #type:ignore
    for att in dir(cls):
        method = getattr(cls ,att,None)
        if method is not None and callable(method) and getattr(method,"_allowedMethod",False):
            cls._allowedHandlers[att] = method#type:ignore
        #------------------
    #------------------
    return cls
#------------------