from typing import Generic, Tuple, TypeVar, TypedDict
from rest_framework import serializers
from web_socket.Handlers.Chat.types.messageStatus import seenStatus
from core.models.Exams_models import Messages, chatRoom


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
        return [
            i 
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
T = TypeVar("T")
class ContentWrapper_D(TypedDict,Generic[T]):
    endpoint:str
    sendTo_groupID:list[chatRoom]
    message:T
#------------------
class ContentWrapper_S(serializers.Serializer): #from-frontend
    endpoint = serializers.CharField()
    sendTo_groupID = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset = chatRoom.objects.all(),
        many=True
    )
    message = serializers.JSONField()
#------------------
class channelEvent(TypedDict,Generic[T]):
    type:str
    message:T
#------------------