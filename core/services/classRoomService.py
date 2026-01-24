from typing import cast
from core.models.Exams_models import ClassRoomAttachment, Exam, Privileges, chatRoom, classRoom
from core.services.types.questionType import GeneralOutput
from core.services.types.userType import IUserHelper
from core.services.utils.classRoomTypes import ClassRoomFromFrontend
from core.services.utils.generalOutputHelper import GOutput
from core.services.utils.priviliages import UserPrivileges
import magic
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from core.services.utils.allowedFormates import ALLOWED_MIME_TYPES

class classRoomService:
    def __init__(self,user) -> None:
        self.Requester:IUserHelper = cast(IUserHelper,user)
    #------------------
    def _RequesterValidation(self,classRoom:classRoom,attribute:UserPrivileges)->GeneralOutput:
        if not classRoom:
            return GOutput(issuccess=False)
        if self.Requester == classRoom.OwnedBy:
            return GOutput(issuccess=True)
        RequesterPrivileges = self.Requester.Privileges.filter(classRoom=classRoom).first()
        if not RequesterPrivileges:
            return GOutput(error={"unauthorized":"cannot access this resource"})
        if RequesterPrivileges.Privilege & attribute != 0:
            return GOutput(issuccess=True)
        else:
            paidClassRoom = self.Requester.Payment_classRoom.filter(classRoom=classRoom).first()
            if paidClassRoom:
                return GOutput(issuccess=True)
            #------------------
        #------------------
        return GOutput(error={"unauthorized":"cannot access this resource"})
    #------------------
    def editSettings(self,currentRoom:classRoom,body:ClassRoomFromFrontend)->GeneralOutput:
        if not self._RequesterValidation(currentRoom,UserPrivileges._OWNER_PRIVILEGES)["isSuccess"]:
            return GOutput(error={"settings":"cannot set setting from null owner"})
        #------------------
        if not body:
            return GOutput(error={"settings":"cannot set setting from null owner"})
        #------------------
        changed = False
        if body["paymentAmount"] and currentRoom.paymentAmount != body["paymentAmount"]:
            currentRoom.paymentAmount = body["paymentAmount"]
            changed =True
        #------------------
        if body["PaymentExpireInterval_MIN"] and currentRoom.PaymentExpireInterval_MIN != body["PaymentExpireInterval_MIN"]:
            currentRoom.PaymentExpireInterval_MIN = body["PaymentExpireInterval_MIN"]
            changed =True
        #------------------
        if body["PaymentAccessMaxCount"] and currentRoom.PaymentAccessMaxCount != body["PaymentAccessMaxCount"]:
            currentRoom.PaymentAccessMaxCount = body["PaymentAccessMaxCount"]
            changed = True
        #------------------
        if body["HideFromSearch"] and currentRoom.HideFromSearch != body["HideFromSearch"]:
            currentRoom.HideFromSearch = body["HideFromSearch"]
            changed = True
        #------------------
        if body["title"] and currentRoom.Title != body["title"]:
            currentRoom.Title = body["title"]
            changed = True
        #------------------
        if changed:
            currentRoom.save()
        #------------------
        return GOutput(issuccess=changed)
    #------------------
    def createClassRoom(self,body:ClassRoomFromFrontend)->GeneralOutput:
        if not "title" in body:
            return GOutput(error={"title":"cannot be null"})
        #------------------
        if not "HideFromSearch" in body:
            return GOutput(error={"HideFromSearch":"cannot be null"})
        #------------------
        if not "paymentAmount" in body:
            return GOutput(error={"paymentAmount":"cannot be null"})
        #------------------
        if not "PaymentExpireInterval_MIN" in body:
            return GOutput(error={"PaymentExpireInterval_MIN":"cannot be null"})
        #------------------
        if not "PaymentAccessMaxCount" in body:
            return GOutput(error={"PaymentAccessMaxCount":"cannot be null"})
        #------------------
        mainchatRoom = chatRoom.objects.create(
            Name="Main Room",
            paymentAmount=0,
            PaymentExpireInterval_MIN=0,
            PaymentAccessMaxCount=0
        )
        classRoom.objects.create(
            OwnedBy=self.Requester,
            HideFromSearch=body["HideFromSearch"],
            Title=body["title"],
            paymentAmount=body["paymentAmount"],
            PaymentExpireInterval_MIN=body["PaymentExpireInterval_MIN"],
            PaymentAccessMaxCount=body["PaymentAccessMaxCount"],
            chatRoom=mainchatRoom
        )
        return GOutput(issuccess=True)
    #------------------
    def defineRoles(self,currentRoom:classRoom,roleTitle,privileges:UserPrivileges)->GeneralOutput:
        if not self._RequesterValidation(currentRoom,UserPrivileges._OWNER_PRIVILEGES)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot define access rules"})
        if not roleTitle:
            return GOutput(error={"roleTitle":"cannot be null"})
        if not privileges:
            return GOutput(error={"privileges":"cannot be null"})
        currentRoom.Privileges.objects.create(
            Name=roleTitle,
            Privilege=privileges
        )
        return GOutput({"success":"Role create successfully"})
    #------------------
    def addUser(self, currentRoom:classRoom,role:Privileges,user:IUserHelper)->GeneralOutput:
        if not self._RequesterValidation(currentRoom,UserPrivileges.ADD_STUDENTS)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot Add User"})
        #------------------
        if not currentRoom.Privileges.objects.contains(role):
            return GOutput(error={"privileges":"cannot add user with a not exist privileges"})
        #------------------
        role.User.add(cast(User,user))
        return GOutput({"success":"user created with specified role successfully"})
    #------------------
    def addExam(self,currentRoom:classRoom,Exam:Exam):
        if not self._RequesterValidation(currentRoom,UserPrivileges.CREATE_EXAM)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot Add or create Exam"})
        if not Exam:
            return GOutput(error={"Exam":"cannot be null"})
        currentRoom.Exams.add(Exam)
    #------------------
    def addAttachment(self,currentRoom:classRoom,file:InMemoryUploadedFile,paymentAmount:float=0,PaymentExpireInterval_MIN:int=0,PaymentAccessMaxCount:int=0)->GeneralOutput:
        if not self._RequesterValidation(currentRoom,UserPrivileges.UPLOAD_ATTACHMENT)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot upload attachement"})
        mimeFile = magic.from_buffer(file.read(2048),mime=True) 
        file.seek(0)
        if not mimeFile in ALLOWED_MIME_TYPES:
            return GOutput(error={"unauthorized":"cannot upload this type of attachments"})
        ClassRoomAttachment.objects.create(
            paymentAmount=paymentAmount,
            PaymentExpireInterval_MIN=PaymentExpireInterval_MIN,
            PaymentAccessMaxCount = PaymentAccessMaxCount,
            Attachments=file,
            classRoom=currentRoom
        )
        return GOutput({"success":"attachment uploaded successfully"})
    #------------------
    def listClassRooms(self,limit:int=100,last_id:int=0)->GeneralOutput:
        classRooms = self.Requester.OwnedClasses.filter(ID__gt=last_id)[:limit].order_by('ID').values('Title','HideFromSearch','OwnedBy','paymentAmount','PaymentExpireInterval_MIN','PaymentAccessMaxCount')
        return GOutput(list(classRooms))
    #------------------
    def listUsersWithPrivileges(self,currentClassRoom:classRoom,privilege:UserPrivileges,limit:int=100,last_id:int=0):
        if not self._RequesterValidation(currentClassRoom,UserPrivileges.LIST_STUDENTS):
            return GOutput(error={"unauthorized":"cannot access this classRoom"})
        currentPriv = currentClassRoom.Privileges.objects.filter(Privilege=privilege).first()
        if not currentPriv:
            return GOutput(error={"privilege":"not exist privilege"})
        #------------------
        users = currentPriv.User.filter(ID__gt=last_id).order_by('ID')[:limit].values('ID', 'username', 'email')
        return GOutput(list(users))
    #------------------
    def listPrivileges(self,currentClassRoom:classRoom)->GeneralOutput:
        if not self._RequesterValidation(currentClassRoom,UserPrivileges.LIST_STUDENTS):
            return GOutput(error={"unauthorized":"cannot access this classRoom"})
        return GOutput(list(currentClassRoom.Privileges.objects.values('Name','id')))
    #------------------
#------------------CLASS_ENDED#------------------