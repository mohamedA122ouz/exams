from typing import cast
from core.models.Exams_models import ClassRoomAttachment, Exam, Privileges, chatRoom, classRoom
from core.services.types.questionType import GeneralOutput
from core.services.types.userType import IUserHelper
from core.services.utils.generalOutputHelper import GOutput
from core.services.utils.priviliages import UserPrivileges
import magic
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from utils.allowedFormates import ALLOWED_MIME_TYPES

class classRoomService:
    def __init__(self,user) -> None:
        self.Requester:IUserHelper = cast(IUserHelper,user)
    #------------------
    def _RequesterValidation(self,classRoom:classRoom,attribute:UserPrivileges)->GeneralOutput:
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
    def editSettings(self,currentRoom:classRoom,paymentAmount:int,PaymentExpireInterval_MIN:int,PaymentAccessMaxCount:int,HideFromSearch:bool):
        if not self._RequesterValidation(currentRoom,UserPrivileges._OWNER_PRIVILEGES):
            return GOutput(error={"settings":"cannot set setting from non owner"})
        #------------------
        changed = False
        if currentRoom.paymentAmount != paymentAmount:
            currentRoom.paymentAmount = paymentAmount
            changed =True
        #------------------
        if currentRoom.PaymentExpireInterval_MIN != PaymentExpireInterval_MIN:
            currentRoom.PaymentExpireInterval_MIN = PaymentExpireInterval_MIN
            changed =True
        #------------------
        if currentRoom.PaymentAccessMaxCount != PaymentAccessMaxCount:
            currentRoom.PaymentAccessMaxCount = PaymentAccessMaxCount
            changed = True
        #------------------
        if currentRoom.HideFromSearch != HideFromSearch:
            currentRoom.HideFromSearch = HideFromSearch
            changed = True
        #------------------
        if changed:
            currentRoom.save()
        #------------------
        return GOutput(issuccess=changed)
    #------------------
    def createClassRoom(self,title:str,HideFromSearch:bool=True,paymentAmount:float=0,PaymentExpireInterval_MIN:int=0,PaymentAccessMaxCount:int=0)->GeneralOutput:
        mainchatRoom = chatRoom.objects.create(
            Name="Main Room",
            paymentAmount=0,
            PaymentExpireInterval_MIN=0,
            PaymentAccessMaxCount=0
        )
        mainRoom = classRoom.objects.create(
            OwnedBy=self.Requester,
            HideFromSearch=HideFromSearch,
            Title=title,
            paymentAmount=paymentAmount,
            PaymentExpireInterval_MIN=PaymentExpireInterval_MIN,
            PaymentAccessMaxCount=PaymentAccessMaxCount,
            chatRoom=mainchatRoom
        )
        return GOutput(issuccess=True)
    #------------------
    def defineRoles(self,currentRoom:classRoom,roleTitle,privileges:UserPrivileges):
        if not self._RequesterValidation(currentRoom,UserPrivileges._OWNER_PRIVILEGES):
            return GOutput(error={"unauthorized":"cannot define access rules"})
        currentRoom.Privileges.objects.create(
            Name=roleTitle,
            Privilege=privileges
        )
        return GOutput({"success":"Role create successfully"})
    #------------------
    def addUser(self, currentRoom:classRoom,role:Privileges,user:IUserHelper):
        if not self._RequesterValidation(currentRoom,UserPrivileges.ADD_STUDENTS):
            return GOutput(error={"unauthorized":"cannot Add User"})
        #------------------
        if not currentRoom.Privileges.objects.contains(role):
            return GOutput(error={"privileges":"cannot add user with a not exist privileges"})
        #------------------
        role.User.add(cast(User,user))
        return GOutput({"success":"user created with specified role successfully"})
    #------------------
    def addExam(self,currentRoom:classRoom,Exam:Exam):
        if not self._RequesterValidation(currentRoom,UserPrivileges.CREATE_EXAM):
            return GOutput(error={"unauthorized":"cannot Add or create Exam"})
        currentRoom.Exams.add(Exam)
    #------------------
    def addAttachment(self,currentRoom:classRoom,file:InMemoryUploadedFile,paymentAmount:float=0,PaymentExpireInterval_MIN:int=0,PaymentAccessMaxCount:int=0):
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

#------------------CLASS_ENDED#------------------