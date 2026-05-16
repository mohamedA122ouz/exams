from typing import Generic, Tuple, TypeVar, TypedDict
from rest_framework import serializers
from web_socket.Handlers.Chat.types.messageStatus import seenStatus
from core.models.Exams_models import Messages, ProfileSettings, chatRoom
from django.contrib.auth.models import User

class sendMessage_S(serializers.ModelSerializer):
    senderID = serializers.SlugRelatedField(
        queryset=ProfileSettings.objects.all(),
        slug_field='profileID',  # This is the field in your DB to check against
    )
    
    senderName = serializers.StringRelatedField(source="sender.username")
    status_text = serializers.SerializerMethodField("statusText",source="status")
    MessageDOMID = serializers.CharField(required=False)
    readbyList = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        read_only=True
    )
    def statusText(self,obj:int):
        try:
            choices:list[Tuple[int,str]] = seenStatus.choices()
            return [
                i 
                for i in choices
                if i[0] == obj["status"]
            ].pop()[0] #type:ignore
        except IndexError:
            return seenStatus.PENDING.value
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
            "readbyList",
            "MessageDOMID"
        ]
    #------------------
    def to_representation(self, instance):
        # This gets the original dictionary of data
        representation = super().to_representation(instance)
        
        # Manually force the profileSettings object to be its profileID string
        if "senderID" in instance:
            representation['senderID'] = str(instance["senderID"].profileID)
            
        return representation
#------------------
# Send Message
class sentMessage_D(TypedDict):
    senderID:str
    senderName:str
    ID:int
    text:str
    createDate:str
    updateDate:str
    status:int #seenStatus
    status_text:str
    MessageDOMID:str
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
    message = serializers.JSONField(required=False)
#------------------
class channelEvent(TypedDict,Generic[T]):
    type:str
    message:T
#------------------