from typing import Literal, Tuple, TypedDict
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
class ContentWrapper_D(TypedDict):
    endpoint:str
    sendTo_groupID:list[chatRoom]
    type:Literal["Event","Message"]
    message:"sentMessage_D"
#------------------
class ContentWrapper_S(serializers.Serializer):
    endpoint = serializers.CharField()
    sendTo_groupID = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset = chatRoom.objects.all(),
        many=True
    )
    type = serializers.ChoiceField(choices=[("Event","Event"),("Message","Message")])
    message = sendMessage_S()
#------------------

