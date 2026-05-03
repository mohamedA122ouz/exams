from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING, Tuple, TypedDict
from rest_framework import serializers
from core.services.types.userType import IUserHelper
from web_socket.Handlers.Chat.types.messageStatus import seenStatus
from core.models.Exams_models import Messages

# Send Message

class sentMessage_D(TypedDict):
    senderID:int
    senderName:str
    ID:int
    text:str
    createDate:str
    updateDate:str
    status:seenStatus
    readbyList:dict
#------------------
class sendMessage_S(serializers.ModelSerializer):
    senderID = serializers.IntegerField(source="sender.id")
    senderName = serializers.StringRelatedField(source="sender.username")
    status_text = serializers.SerializerMethodField("status",source="status")
    def status(self,obj:int):
        choices:list[Tuple[int,str]] = seenStatus.choices()
        return [i 
                for i in choices
                if i[0] == obj
            ][0]
    #------------------
    class Meta:#type:ignore
        model = Messages
        fields=[
            "senderID",
            "senderName",
            "ID",
            "text",
            "createDate",
            "updateDate",
            "status",
            "status_text",
            "readbyList"
        ]
    #------------------
#------------------
# Chat events
class EventType(StrEnum):
    TYPING = "TYPING"
    RECORDING = "RECORDING"
    CALLING = "CALLING"
    UPLOADING = "UPLOADING"
    SEEN = "SEEN"
    RECEIVED = "RECEIVED"
#------------------

class ChatEvent_D(TypedDict):
    senderName:str
    senderID:int
    event:EventType
    MessageID:int
#------------------

