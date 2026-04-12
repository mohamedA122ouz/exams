from typing import TypedDict, Optional
from rest_framework import serializers
from django.contrib.auth.models import User
from core.models.Exams_models import ClassRoomAttachment, Privileges, classRoom
from core.services.utils.privileges import UserPrivileges


class GETREQ_listPrivileges(serializers.Serializer):
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=classRoom.objects.all(),
    )
#---------------
class GETREQ_listPrivileges_Type(TypedDict):
    classroom:classRoom
#---------------
class POSTREQ_addUser(serializers.Serializer):
    privileges = serializers.PrimaryKeyRelatedField(
        queryset=Privileges.objects.all()
    )
    users = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=classRoom.objects.all(),
    )
#---------------
class POSTREQ_addUser_Type(TypedDict):
    classroom:classRoom
    privileges:Privileges
    users:list[User]
#---------------
class POSTREQ_addPrivilegess(serializers.Serializer):
    title = serializers.CharField(required=True)
    privileges = serializers.IntegerField(max_value=UserPrivileges._OWNER_PRIVILEGES,min_value=UserPrivileges.CREATE_EXAM,required=True)
    users = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=classRoom.objects.all(),
        required=True
    )
#---------------
class POSTREQ_addPrivilegess_Type(TypedDict):
    title:str
    classroom:classRoom
    privileges:int
    users:Optional[list[User]]
#---------------
class View_ShowClassRoom(serializers.ModelSerializer):
    OwnedBy = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
        source="OwnedBy.username",
    )
    createdAt = serializers.DateField(
        source="createAt",
    )
    class Meta: #type:ignore
        model=classRoom
        fields = ['Title','OwnedBy','ID','createdAt']
    #---------------
#---------------

class View_ShowClassRoom_Attahcments(serializers.ModelSerializer):
    class Meta:#type:ignore
        model = ClassRoomAttachment
        fields = [
            'name',
            'order',
            'classRoom',
            'attachmentLicence',
            'thumbnail'
        ]
    #---------------
#---------------
class GETREQ_Privileges(serializers.ModelSerializer):
    ID = serializers.IntegerField(
        source='id',
        required=True
    )
    Privilege = serializers.IntegerField(
        read_only=True
    )
    class Meta:#type:ignore
        model = Privileges
        fields = [
            "Name",
            "ClassRooms",
            "Users",
            "Privilege",
            'ID'
        ]
        read_only_fields = ['Name', 'ClassRooms', 'Users', 'Privilege']
    #---------------
#---------------
class GETREQ_Privileges_TYPE(TypedDict):
    Name:str
    ClassRooms:"classRoom"
    Users:User
    Privilege:int
    ID:int
#---------------