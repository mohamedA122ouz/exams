from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING, Tuple, TypedDict
from rest_framework import serializers
from core.services.types.userType import IUserHelper
from web_socket.Handlers.Chat.types.messageStatus import seenStatus
from core.models.Exams_models import Messages
from django.contrib.auth.models import User


class sendMessage_S(serializers.ModelSerializer):
    senderID = serializers.IntegerField(source="sender.id")
    senderName = serializers.StringRelatedField(source="sender.username")
    status_text = serializers.SerializerMethodField("status",source="status")
    readbyList = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,  # Allows you to omit the field in the request
        read_only=True
    )
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
        read_only_fields = [
            'createDate',
            'updateDate'
        ]
    #------------------
#------------------
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
class messageWrapper_D(TypedDict):
    endpoint:str
    message:"sentMessage_D"
#------------------
class messageWrapper_S(serializers.Serializer):
    endpoint = serializers.CharField()
    message = sendMessage_S()
#------------------

