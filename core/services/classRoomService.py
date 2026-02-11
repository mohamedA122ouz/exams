from datetime import datetime
from math import ceil
from typing import Optional, cast

from django.forms import model_to_dict
from core.models.Exams_models import AttachmentLicence, ClassRoomAttachment, Committe, CommitteAllowedList, Exam, Payment_classRoom, Privileges, WatchHistory, chatRoom, classRoom, dependenciesRepo
from core.services.types.questionType import GeneralOutput
from core.services.types.userType import IUserHelper
from core.services.utils import priviliages
from core.services.utils.classRoomTypes import ClassRoomFromFrontend
from core.services.utils.generalOutputHelper import GOutput
from core.services.utils.priviliages import UserPrivileges
import magic
import hashlib
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from core.services.utils.allowedFormates import ALLOWED_MIME_TYPES
from django.db.models import F,ExpressionWrapper,IntegerField,Q

class classRoomService:
    def __init__(self,user) -> None:
        self.Requester:IUserHelper = cast(IUserHelper,user)
    #------------------
    def _RequesterValidation(self,class_room:int|classRoom,privilege:UserPrivileges,countAccessCounterDown:bool=False)->GeneralOutput[Optional[classRoom]]:
        """For Resources that is allowed to be accessed if user paid"""
        wantedClassRoom:Optional[classRoom] = class_room if isinstance(class_room,classRoom) else classRoom.objects.filter(classRoom__ID=class_room).first()
        if not wantedClassRoom:
            return GOutput(error={"404":"classRoom not found"})
        if wantedClassRoom.OwnedBy == self.Requester:
            return GOutput(wantedClassRoom)
        if wantedClassRoom.paymentAmount == 0:
            return GOutput(wantedClassRoom)
        payment = Payment_classRoom.objects.filter(Owner=self.Requester,classRoom=wantedClassRoom).order_by('TransactionTime').first()
        if not payment:
            return GOutput(error={"unauthorized":"cannot access this resource"})
        if not payment.ExpireDateTime and not payment.AccessCounter:
            return GOutput(wantedClassRoom)
        if payment.ExpireDateTime <= datetime.now() and not payment.AccessCounter:
            return GOutput(wantedClassRoom)
        if not payment.ExpireDateTime and payment.AccessCounter > 0:
            if countAccessCounterDown:
                payment.AccessCounter -= 1
                payment.save()
            return GOutput(wantedClassRoom)
        #------------------
        if payment.ExpireDateTime <= datetime.now() and payment.AccessCounter > 0:
            if countAccessCounterDown:
                payment.AccessCounter -= 1
                payment.save()
            return GOutput(wantedClassRoom)
        #------------------
        checkingResult = self._checkForPrivilege(wantedClassRoom,privilege)
        if checkingResult["isSuccess"]:
            return GOutput(checkingResult["output"])
        return GOutput(error={"unauthorized":"cannot access this resource"})
    #------------------
    def accessClassRoom(self,classRoom:classRoom|int)->GeneralOutput:
        return self._RequesterValidation(classRoom,UserPrivileges.ACCESS_CLASSROOM_WITHOUT_PAYING,True)
    #------------------
    def _checkForPrivilege(self,class_room:int|classRoom,privilege:UserPrivileges):
        """for checking for resources only witout the payment stuff"""
        wantedClassRoom:Optional[classRoom] = class_room if isinstance(class_room,classRoom) else classRoom.objects.filter(classRoom__ID=class_room).first()
        userprivilege = self.Requester.Privileges.filter(ClassRoom=wantedClassRoom).all() if isinstance(class_room,classRoom) else self.Requester.Privileges.filter(ClassRoom__ID=class_room).all()
        userprivilege = [priv for priv in userprivilege if priv.Privilege & privilege != 0]
        if len(userprivilege) > 0:
            return GOutput(wantedClassRoom)
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
        currentRoom.Privileges.create(
            Name=roleTitle,
            Privilege=privileges
        )
        return GOutput({"success":"Role create successfully"})
    #------------------
    def addUser(self, currentRoom:classRoom,role:Privileges,user:IUserHelper)->GeneralOutput:
        if not self._RequesterValidation(currentRoom,UserPrivileges.ADD_STUDENTS)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot Add User"})
        #------------------
        if not currentRoom.Privileges.contains(role):
            return GOutput(error={"privileges":"cannot add user with a not exist privileges"})
        #------------------
        role.Users.add(cast(User,user))
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
        hasher = hashlib.sha256()
        for chunk in iter(lambda: file.read(8192), b""):
            hasher.update(chunk)
        file.seek(0)
        file_hash = hasher.hexdigest()
        fileLicence = AttachmentLicence.objects.filter(FileFingerPrint=file_hash).first()
        if not fileLicence:
            fileLicence = AttachmentLicence.objects.create(
                FileFingerPrint = file_hash,
                RequireSecurity=True
            )
            ClassRoomAttachment.objects.create(
                paymentAmount=paymentAmount,
                PaymentExpireInterval_MIN=PaymentExpireInterval_MIN,
                PaymentAccessMaxCount = PaymentAccessMaxCount,
                Attachments=file,
                classRoom=currentRoom,
                attachmentLicence = fileLicence
            )
            return GOutput({"success":"attachment uploaded successfully"})
        #------------------
        if not fileLicence.owner != self.Requester:
            self.Requester.Settings.Warnings -= 1 #type:ignore
            self.Requester.Settings.save() #type:ignore
            return GOutput({"unauthorized":f"cannot upload this attachment you have {self.Requester.Settings.Warnings}-warning remains"}) #type:ignore
        classRoom.Attachments.add(fileLicence.classRoomAttachment)
        return GOutput({"success":f"file uploaded successfully **warning: you already have this file uploaded on the system"})
    #------------------
    def listClassRooms(self,limit:int=100,last_id:int=0)->GeneralOutput:
        classRooms = self.Requester.OwnedClasses.filter(ID__gt=last_id)[:limit].order_by('ID').values('Title','HideFromSearch','OwnedBy','paymentAmount','PaymentExpireInterval_MIN','PaymentAccessMaxCount')
        return GOutput(list(classRooms))
    #------------------
    def listUsersWithPrivileges(self,currentClassRoom:classRoom,privilege:UserPrivileges,limit:int=100,last_id:int=0):
        if not self._RequesterValidation(currentClassRoom,UserPrivileges.LIST_STUDENTS)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this classRoom"})
        currentPriv = currentClassRoom.Privileges.filter(Privilege=privilege).first()
        if not currentPriv:
            return GOutput(error={"privilege":"not exist privilege"})
        #------------------
        users = currentPriv.Users.filter(ID__gt=last_id).order_by('ID')[:limit].values('ID', 'username', 'email')
        return GOutput(list(users))
    #------------------
    def listPrivileges(self,currentClassRoom:classRoom)->GeneralOutput:
        if not self._RequesterValidation(currentClassRoom,UserPrivileges.LIST_STUDENTS)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this classRoom"})
        return GOutput(list(currentClassRoom.Privileges.values('Name','id')))
    #------------------
    def listAttachments(self,currentClassRoom:classRoom):
        if not self._RequesterValidation(currentClassRoom,UserPrivileges.ACCESS_ATTACHMENT_WITHOUT_PAYING)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this functionallity on classRoom"})
        return GOutput(list(currentClassRoom.Attachments.values('name','ID')))
    #------------------
    def showAttahcment(self,currentClassRoom:classRoom,AttahcmentID:int):
        if not self._RequesterValidation(currentClassRoom,UserPrivileges.ACCESS_ATTACHMENT_WITHOUT_PAYING)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this functionallity on classRoom"})
        cl_att = classRoom.Attachments.filter(ID=AttahcmentID).first()
        isVerified = False
        if not cl_att:
            return GOutput(error={"404":"cannot access this attachment"})
        if not cl_att.isOrdered or cl_att.order == 1:
            isVerified = True
        #------------------
        history = self.Requester.attachmentHistory.filter(attachment__order__lte=cl_att.order,attachment__classRoom=currentClassRoom)
        if history.exists() :
            isVerified = True
        #------------------
        if cl_att.dependencies.exists():
            isVerified = False
            if self._checkDependencies(cl_att):
                isVerified = True
            #------------------
        #------------------
        if isVerified:
            self.Requester.attachmentHistory.create(attachment=cl_att)
            return GOutput({
                "name":cl_att.name,
                "ID":cl_att.ID,
                "Attachments":[{'name':att.name,'ID':att.ID,'Attachments_Count':len(att.Attachments)}for att in cl_att.Attachments]
            })
        #------------------
        return GOutput(error={"400":"bad request cannot access this resource without order"})
    #------------------
    def _checkDependencies(self,attachment:ClassRoomAttachment):
        deps = attachment.dependencies.all()
        repoItems = dependenciesRepo.objects.filter(field_value__in=deps)
        if len(deps) != len(repoItems):
            return False
        #------------------
        for dep in deps:
            ...
    #------------------
    def AutocreateCommitee(self,currentClassRoom:classRoom,Exam:Exam):
        if not self._checkForPrivilege(currentClassRoom,UserPrivileges.CREATE_EXAM)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this functionallity on classRoom"})
        #------------------
        privileges = currentClassRoom.Privileges.all()
        adminPrivileges = [priv for priv in privileges if priv.Privilege & UserPrivileges.CREATE_EXAM.value]
        studentsPrivileges = [priv for priv in privileges if priv.Privilege & UserPrivileges.SOLVE_EXAM_ALLOWANCE.value]
        admins = []
        for user in adminPrivileges:
            admins += list(user.Users.all())
        #------------------
        students = []
        for user in studentsPrivileges:
            students += list(user.Users.all())
        #------------------
        adminsCount = len(admins)
        studentsCount = len(students)
        CommitteStudentsCount = ceil(studentsCount/adminsCount)
        committes:list[Committe] = []
        for admin in admins:
            committes.append(Committe(
                clRoom = currentClassRoom,
                Exam = Exam,
                isOpened = False,
                inspector = admin
            ))
        #------------------
        Committe.objects.bulk_create(committes)
        allCommittesLists = []
        for i,committe in enumerate(committes):
            start = i * CommitteStudentsCount
            end = start + CommitteStudentsCount - 1
            allCommittesLists += [CommitteAllowedList(users=st,committe=committe,present=False) for st in students[start:end]]
        #------------------
        CommitteAllowedList.objects.bulk_create(allCommittesLists)
    #------------------
    def ManualcreateCommitee(self,currentClassRoom:classRoom,Exam:Exam,admins:list[IUserHelper]):
        if not self._checkForPrivilege(currentClassRoom,UserPrivileges.CREATE_EXAM)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this functionallity on classRoom"})
        #------------------
        privileges = currentClassRoom.Privileges.all()
        studentsPrivileges = [priv for priv in privileges if priv.Privilege & UserPrivileges.SOLVE_EXAM_ALLOWANCE.value]
        students = []
        for user in studentsPrivileges:
            students += list(user.Users.all())
        #------------------
        adminsCount = len(admins)
        studentsCount = len(students)
        CommitteStudentsCount = ceil(studentsCount/adminsCount)
        committes:list[Committe] = []
        for admin in admins:
            committes.append(Committe(
                clRoom = currentClassRoom,
                Exam = Exam,
                isOpened = False,
                inspector = admin
            ))
        #------------------
        Committe.objects.bulk_create(committes)
        allCommittesLists = []
        for i,committe in enumerate(committes):
            start = i * CommitteStudentsCount
            end = start + CommitteStudentsCount - 1
            allCommittesLists += [CommitteAllowedList(users=st,committe=committe,present=False) for st in students[start:end]]
        #------------------
        CommitteAllowedList.objects.bulk_create(allCommittesLists)
    #------------------
#------------------CLASS_ENDED#------------------