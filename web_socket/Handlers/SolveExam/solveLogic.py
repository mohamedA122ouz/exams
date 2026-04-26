from typing import TYPE_CHECKING, TypedDict
from django.core.cache import cache

if TYPE_CHECKING:
    from channels.generic.websocket import AsyncJsonWebsocketConsumer
    
    class AddRowEvent(TypedDict):
        userID:int
        location:list[float]
        committeeID:int
    #---------------
    
class CommitteeLogic:
    
    def Exam_addRow(self:"AsyncJsonWebsocketConsumer",event:AddRowEvent):
        cache.set()