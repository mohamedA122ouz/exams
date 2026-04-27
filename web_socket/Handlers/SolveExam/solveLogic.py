from typing import TYPE_CHECKING, TypedDict
from channels.db import database_sync_to_async
from channels.layers import channel_layers
from django.core.cache import cache
from core.models.Exams_models import CommitteAllowedList
from core.services.utils.generalOutputHelper import GOutput
from asgiref.sync import async_to_sync

if TYPE_CHECKING:
    from core.services.types.questionType import GeneralOutput
    from core.services.types.userType import IUserHelper
    from channels.generic.websocket import AsyncJsonWebsocketConsumer
    
    class AddRowEvent(TypedDict):
        userID:int
        location:list[float]
        committeeID:int
    #---------------
    
class CommitteeLogic:
    stndsCounterKey = "studentsCounter"
    RowIdKey = "CommittteeRow"
    #Exam Committee connect
    @database_sync_to_async
    def Committee_Connect(self:"AsyncJsonWebsocketConsumer",user:IUserHelper,committee:int)->GeneralOutput:#type:ignore
        counter = cache.get(CommitteeLogic.stndsCounterKey,0)
        RowID = cache.get(CommitteeLogic.RowIdKey,0)
        if counter % 256 == 0:
            RowID += 1
        #------------------
        counter += 1
        try:
            currentCommittee = user.allowedIn.get(committe=committee)
            if not currentCommittee:
                return GOutput(error={"unauthorized":"cannot access this resource"})
            async_to_sync(self.channel_layer.group_add)(f"R:{RowID},C:{currentCommittee.id}",self.channel_name) #type:ignore
            return GOutput({"success":"user is connected to the commitee successfully"})
        except CommitteAllowedList.DoesNotExist:
            return GOutput({"success":"user is connected to the commitee successfully"})
    #------------------
