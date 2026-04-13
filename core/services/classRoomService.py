from datetime import datetime
from math import ceil
from typing import Optional, cast
from core.models.Exams_models import AttachmentLicence, ClassRoomAttachment, Committe, CommitteAllowedList, Exam, Payment_Attachment, Payment_classRoom, Privileges, WatchHistory, chatRoom, classRoom, classRoom_ClassRoomAttachment, dependenciesRepo, shareWithLink
from core.services.types.questionType import GeneralOutput
from core.services.types.userType import IUserHelper
from core.services.utils.classRoomTypes import ClassRoomFromFrontend
from core.services.utils.commands import Commands
from core.services.utils.dependencieChecker import DependenciesAnalyzer
from core.services.utils.generalOutputHelper import GOutput
from core.services.utils.openBaseNumber import Base62
from core.services.utils.privileges import UserPrivileges
import magic
import hashlib
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from core.services.utils.allowedFormates import ALLOWED_MIME_TYPES
from django.db import transaction
from django.db.models import F
from core.services.utils.viewSerializers import GETREQ_Privileges, GETREQ_Privileges_TYPE, View_ShowClassRoom
from django.db.models import QuerySet


class classRoomService:
    def __init__(self,user) -> None:
        self.Requester:IUserHelper = cast(IUserHelper,user)
        self.UNAUTHORIZED_OBJECT = {"unauthorized":"cannot access this resource"}
        self.NOT_FOUND = {"classRoom":"is not found"}
    #---------------
        # Security_Layer1
    def _UserExists(self,class_room:classRoom)->bool:
        allPrivileges = class_room.Privileges.all()
        users = [p.Users for p in allPrivileges]
        return self.Requester in users
    #---------------
    # Security_Layer2
    def _checkForPrivilege(self,class_room:int|classRoom,privilege:UserPrivileges):
        """for checking for resources only without the payment stuff
        DON'T USE OWNER_PRIVILEGES HERE THIS WILL RETURN TRUE FOR ALL ITEMS IT IS LIKE WHILE TRUE HERE
        """
        wantedClassRoom:Optional[classRoom] = class_room if isinstance(class_room,classRoom) else classRoom.objects.filter(ID=class_room).first()
        userprivilege = self.Requester.Privileges.filter(ClassRooms=wantedClassRoom).all() if isinstance(class_room,classRoom) else self.Requester.Privileges.filter(ClassRooms__ID=class_room).all()
        userprivilege = [priv for priv in userprivilege if priv.Privilege & privilege != 0]
        if len(userprivilege) > 0:
            return GOutput(wantedClassRoom)
        return GOutput(error={"unauthorized":"cannot access this resource"})
    #---------------
    def _AccessClassRoom(self,class_room:int|classRoom,privilege:UserPrivileges,countAccessCounterDown:bool=False)->GeneralOutput[Optional[classRoom]]:
        """For Resources that is allowed to be accessed if user paid
        USING OWNER_PRIVILEGES HERE IS LIKE ONLY ACCESS IF YOU ARE THE OWNER
        """
        wantedClassRoom:Optional[classRoom] = class_room if isinstance(class_room,classRoom) else classRoom.objects.filter(ID=class_room).first()
        if not wantedClassRoom:
            return GOutput(error={"classRoom":"not found"})
        if wantedClassRoom.OwnedBy == self.Requester:
            return GOutput(wantedClassRoom)
        if privilege == UserPrivileges._OWNER_PRIVILEGES and self.Requester == wantedClassRoom.OwnedBy:
            return GOutput(wantedClassRoom)
        elif privilege == UserPrivileges._OWNER_PRIVILEGES:
            return GOutput(error=self.UNAUTHORIZED_OBJECT)
        checkingResult = self._checkForPrivilege(class_room,privilege)
        if not checkingResult["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this resource"})
        if wantedClassRoom.paymentAmount == 0:
            return GOutput(wantedClassRoom)

        payment = Payment_classRoom.objects.filter(Owner=self.Requester,Privilege__ClassRooms=wantedClassRoom).order_by('TransactionTime').first()
        if not payment:
            return GOutput(error={"unauthorized":"cannot access this resource"})
        if not payment.ExpireDateTime and not payment.AccessCounter:
            return GOutput(wantedClassRoom)
        if payment.ExpireDateTime.replace(tzinfo=None) >= datetime.now() and payment.Amount == wantedClassRoom.paymentAmount and not payment.AccessCounter:
            return GOutput(wantedClassRoom)
        if not payment.ExpireDateTime.replace(tzinfo=None) and payment.AccessCounter > 0:
            if countAccessCounterDown:
                payment.AccessCounter -= 1
                payment.save()
            return GOutput(wantedClassRoom)
        #---------------
        if payment.ExpireDateTime.replace(tzinfo=None) >= datetime.now() and payment.Amount == wantedClassRoom.paymentAmount and payment.AccessCounter > 0:
            if countAccessCounterDown:
                payment.AccessCounter -= 1
                payment.save()
            return GOutput(wantedClassRoom)
        #---------------
        if self._checkForPrivilege(class_room,UserPrivileges.ACCESS_CLASSROOM_WITHOUT_PAYING)["isSuccess"]:
            return GOutput(wantedClassRoom)
        return GOutput(error={"unauthorized":"cannot access this resource"})
    #---------------
    def accessClassRoom(self,classRoom:classRoom|int)->GeneralOutput[Optional[classRoom]]:
        return self._AccessClassRoom(classRoom,UserPrivileges.ACCESS_CLASSROOM_WITHOUT_PAYING,True)
    #---------------
    def PrivilegeDetials(self,privilege_ID:int):
        model = Privileges.objects.filter(id=privilege_ID).first()
        serializer = GETREQ_Privileges(model)
        data:GETREQ_Privileges_TYPE = serializer.data #type:ignore
        if not self._AccessClassRoom(model.ClassRooms,UserPrivileges._OWNER_PRIVILEGES)["isSuccess"]:#type:ignore
            return GOutput(error=self.UNAUTHORIZED_OBJECT)
        #---------------
        allPrivileges = UserPrivileges.tojson()
        privileges:list[str] = [ pri for pri in allPrivileges if allPrivileges[pri] & data["Privilege"] != 0]
        return GOutput(privileges)
    #---------------
    def editSettings(self,currentRoom:classRoom,body:ClassRoomFromFrontend)->GeneralOutput:
        if not self._AccessClassRoom(currentRoom,UserPrivileges._OWNER_PRIVILEGES)["isSuccess"]:
            return GOutput(error={"settings":"cannot set setting from null owner"})
        #---------------
        if not body:
            return GOutput(error={"settings":"cannot set setting from null owner"})
        #---------------
        changed = False
        if body["paymentAmount"] and currentRoom.paymentAmount != body["paymentAmount"]:
            currentRoom.paymentAmount = body["paymentAmount"]
            changed =True
        #---------------
        if body["PaymentExpireInterval_MIN"] and currentRoom.PaymentExpireInterval_MIN != body["PaymentExpireInterval_MIN"]:
            currentRoom.PaymentExpireInterval_MIN = body["PaymentExpireInterval_MIN"]
            changed =True
        #---------------
        if body["PaymentAccessMaxCount"] and currentRoom.PaymentAccessMaxCount != body["PaymentAccessMaxCount"]:
            currentRoom.PaymentAccessMaxCount = body["PaymentAccessMaxCount"]
            changed = True
        #---------------
        if body["HideFromSearch"] and currentRoom.HideFromSearch != body["HideFromSearch"]:
            currentRoom.HideFromSearch = body["HideFromSearch"]
            changed = True
        #---------------
        if body["title"] and currentRoom.Title != body["title"]:
            currentRoom.Title = body["title"]
            changed = True
        #---------------
        if changed:
            currentRoom.save()
        #---------------
        return GOutput(issuccess=changed)
    #---------------
    @transaction.atomic
    def createClassRoom(self,body:ClassRoomFromFrontend)->GeneralOutput:
        if not "title" in body:
            return GOutput(error={"title":"cannot be null"})
        #---------------
        if not "HideFromSearch" in body:
            return GOutput(error={"HideFromSearch":"cannot be null"})
        #---------------
        if not "paymentAmount" in body:
            return GOutput(error={"paymentAmount":"cannot be null"})
        #---------------
        if not "PaymentExpireInterval_MIN" in body:
            return GOutput(error={"PaymentExpireInterval_MIN":"cannot be null"})
        #---------------
        if not "PaymentAccessMaxCount" in body:
            return GOutput(error={"PaymentAccessMaxCount":"cannot be null"})
        #---------------
        TABLE_NAME ='classRoom'
        createdClassRoom = classRoom.objects.create(
            OwnedBy=self.Requester,
            HideFromSearch=body["HideFromSearch"],
            Title=body["title"],
            paymentAmount=body["paymentAmount"],
            PaymentExpireInterval_MIN=body["PaymentExpireInterval_MIN"],
            PaymentAccessMaxCount=body["PaymentAccessMaxCount"],
            attachmentsCounter = 0
        )
        mainchatRoom = chatRoom.objects.create(
            Name="Main Room",
            paymentAmount=0,
            PaymentExpireInterval_MIN=0,
            PaymentAccessMaxCount=0,
            classRoom=createdClassRoom
        )
        numBase = Base62()
        dt = datetime.now()
        num = numBase.getNumber(f"{TABLE_NAME}{dt.day}{dt.minute}{createdClassRoom.ID}")
        shareWithLink.objects.create(
            tableName=TABLE_NAME,
            address=numBase.convert(num),
            itemID=createdClassRoom.ID,
            command=Commands.JOIN.value
        )
        return GOutput({"success":"classRoom created"})
    #---------------
    def defineRoles(self,currentRoom:classRoom,roleTitle,privileges:UserPrivileges)->GeneralOutput:
        if not self._AccessClassRoom(currentRoom,UserPrivileges._OWNER_PRIVILEGES)["isSuccess"]:
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
    #---------------
    def addUsers(self, currentRoom:classRoom,role:Privileges,users:list[IUserHelper])->GeneralOutput:
        if not self._AccessClassRoom(currentRoom,UserPrivileges.ADD_STUDENTS)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot Add User"})
        #---------------
        if not currentRoom.Privileges.contains(role):
            return GOutput(error={"privileges":"cannot add user with a not exist privileges"})
        #---------------
        # role.Users.add(cast(User,user))
        role.Users.add(*cast(list[User],users))
        return GOutput({"success":"user created with specified role successfully"})
    #---------------
    def showUsers(self,currentRoom:classRoom):
        if not self._AccessClassRoom(currentRoom,UserPrivileges.ADD_STUDENTS | UserPrivileges.REMOVE_STUDNET)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot Add User"})
        #---------------
        if not currentRoom.Privileges:
            return GOutput([])
        #---------------
        users = classRoom.objects.prefetch_related('Privileges__Users').filter(ID=currentRoom.ID).values(
            username=F('Privileges__Users__username'),
            email=F('Privileges__Users__email'),
            first_name=F('Privileges__Users__first_name'),
            last_name=F('Privileges__Users__last_name'),
            id=F('Privileges__Users__id')
        )
        return GOutput( list(users) if isinstance(users,QuerySet) else [])
    #---------------
    def removeUsers(self,currentRoom:classRoom,role:Privileges,users:list[IUserHelper]):
        if not self._AccessClassRoom(currentRoom,UserPrivileges.REMOVE_STUDNET)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot remove User"})
        #---------------
        if not currentRoom.Privileges.contains(role):
            return GOutput(error={"privileges":"cannot remove user with a not exist privileges"})
        #---------------
        role.Users.remove(*cast(list[User],users))
    #---------------
    def addExam(self,currentRoom:classRoom,Exam:Exam):
        if not self._AccessClassRoom(currentRoom,UserPrivileges.CREATE_EXAM)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot Add or create Exam"})
        if not Exam:
            return GOutput(error={"Exam":"cannot be null"})
        currentRoom.Exams.add(Exam)
    #---------------
    def removeExam(self,currentRoom:classRoom,Exam:Exam):
        if not self._AccessClassRoom(currentRoom,UserPrivileges.CREATE_EXAM)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot remove Exam"})
        if not Exam:
            return GOutput(error={"Exam":"cannot be null"})
        currentRoom.Exams.remove(Exam)
    #---------------
    def addAttachment(self,currentRoom:classRoom,file:InMemoryUploadedFile,paymentAmount:float=0,PaymentExpireInterval_MIN:int=0,PaymentAccessMaxCount:int=0)->GeneralOutput:
        if not self._AccessClassRoom(currentRoom,UserPrivileges.UPLOAD_ATTACHMENT)["isSuccess"]:
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
            with transaction.atomic():
                fileLicence = AttachmentLicence.objects.create(
                    FileFingerPrint = file_hash,
                    RequireSecurity=True,
                    owner=self.Requester
                )
                count = currentRoom.attachmentsCounter + 1
                clAtt = ClassRoomAttachment.objects.create(
                    paymentAmount=paymentAmount,
                    PaymentExpireInterval_MIN=PaymentExpireInterval_MIN,
                    PaymentAccessMaxCount = PaymentAccessMaxCount,
                    Attachments=file,
                    attachmentLicence = fileLicence,
                    order=count,
                    isOrdered=False
                )
                classRoom_ClassRoomAttachment.objects.create(
                    classRoom=currentRoom,
                    order=count,
                    isOrderDepenent=True,
                    ClassRoomAttachment=clAtt
                )
                currentRoom.attachmentsCounter = count
                currentRoom.save()
            #---------------
            return GOutput({"success":"attachment uploaded successfully"})
        #---------------
        if not fileLicence.owner != self.Requester:
            self.Requester.Settings.Warnings -= 1 #type:ignore
            self.Requester.Settings.save() #type:ignore
            return GOutput({"unauthorized":f"cannot upload this attachment you have {self.Requester.Settings.Warnings}-warning remains"}) #type:ignore
        classRoom.Attachments.add(fileLicence.classRoomAttachment)
        return GOutput({"success":f"file uploaded successfully **warning: you already have this file uploaded on the system"})
    #---------------
    def listClassRooms(self,limit:int=100,last_id:int=0)->GeneralOutput:
        classRooms = self.Requester.OwnedClasses.order_by('ID').filter(ID__gt=last_id)[:limit].values('ID','Title','HideFromSearch','OwnedBy','paymentAmount','PaymentExpireInterval_MIN','PaymentAccessMaxCount')
        return GOutput(list(classRooms))
    #---------------
    
    def subscripedClassRooms(self,user:IUserHelper,limit:int=100,last_id:int=0)->GeneralOutput:
        allPrivileges = user.Privileges.all()
        classRooms = [privilege.ClassRooms for privilege in allPrivileges]
        viewClassRooms = View_ShowClassRoom(classRooms,many=True)
        return GOutput(viewClassRooms.data)
    #---------------
    def listUsersWithPrivileges(self,privilege:Privileges,limit:int=100,last_id:int=0):
        if not self._AccessClassRoom(privilege.ClassRooms,UserPrivileges.LIST_STUDENTS)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this classRoom"})
        #---------------
        return GOutput(list(privilege.Users.values('id',"username",'first_name','last_name','email')))
    #---------------
    def listPrivileges(self,currentClassRoom:classRoom)->GeneralOutput:
        if not self._AccessClassRoom(currentClassRoom,UserPrivileges.LIST_STUDENTS)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this classRoom"})
        return GOutput(list(currentClassRoom.Privileges.values('Name','id')))
    #---------------
    def _AccessAttachment(self,currentClassRoom:classRoom|int,attachmentID:int):
        classRoomAccessValidation = self._AccessClassRoom(currentClassRoom,UserPrivileges.ACCESS_ATTACHMENT_WITHOUT_PAYING)
        if not classRoomAccessValidation["isSuccess"]:
            return GOutput(error=classRoomAccessValidation["error"])
        #---------------
        attachment = None
        try:
            attachment = ClassRoomAttachment.objects.get(ID=attachmentID)
            payment = Payment_Attachment.objects.filter(Owner=self.Requester,classRoomAttachment=attachment).order_by("TransactionTime").first()
            if not payment:
                raise Payment_Attachment.DoesNotExist
            if payment.ExpireDateTime.replace(tzinfo=None) >= datetime.now() and payment.Amount == attachment.paymentAmount:
                return GOutput(attachment)
        except ClassRoomAttachment.DoesNotExist:
            return GOutput(error={"unauthorized":"cannot access attachment"})
        except Payment_Attachment.DoesNotExist:
            if self._checkForPrivilege(currentClassRoom,UserPrivileges.ACCESS_ATTACHMENT_WITHOUT_PAYING):
                return GOutput(attachment)
        #---------------
    #---------------
    def listAttachments(self,currentClassRoom:classRoom|int):
        author_Output = self._AccessClassRoom(currentClassRoom,UserPrivileges.ACCESS_CLASSROOM_WITHOUT_PAYING|UserPrivileges.SOLVE_EXAM_ALLOWANCE)
        if not author_Output["isSuccess"]:
            return GOutput(error=author_Output["error"])
        wantedClassRoom:classRoom = author_Output["output"] #type:ignore
        return GOutput(list(wantedClassRoom.Attachments.values('name','ID')))
    #---------------
    def showAttahcment(self,currentClassRoom:classRoom,AttahcmentID:int):
        if not self._AccessClassRoom(currentClassRoom,UserPrivileges.ACCESS_ATTACHMENT_WITHOUT_PAYING)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this functionallity on classRoom"})
        cl_att = classRoom.Attachments.filter(ID=AttahcmentID).first()
        isVerified = False
        if not cl_att:
            return GOutput(error={"attachment":"not found"})
        if not cl_att.isOrdered or cl_att.order == 1:
            isVerified = True
        #---------------
        history = self.Requester.attachmentHistory.filter(attachment__order__lte=cl_att.order,attachment__classRoom=currentClassRoom)
        if history.exists() :
            isVerified = True
        #---------------
        if cl_att.dependencies.exists():
            isVerified = False
            if self._checkDependencies(cl_att):
                isVerified = True
            #---------------
        #---------------
        if isVerified:
            self.Requester.attachmentHistory.create(attachment=cl_att)
            return GOutput({
                "name":cl_att.name,
                "ID":cl_att.ID,
                "Attachments":[{'name':att.name,'ID':att.ID,'Attachments_Count':len(att.Attachments)}for att in cl_att.Attachments]
            })
        #---------------
        return GOutput(error={"400":"bad request cannot access this resource without order"})
    #---------------
    def _checkDependencies(self,attachment:ClassRoomAttachment):
        depchecker = DependenciesAnalyzer()
        dependancies = attachment.dependencies.all()
        if len(dependancies) == 0:
            return True
        for dep in dependancies:
            if not depchecker.verify(dep):
                return False
        #---------------
        return True
    #---------------
    def AutocreateCommitee(self,currentClassRoom:classRoom,Exam:Exam):
        if not self._checkForPrivilege(currentClassRoom,UserPrivileges.CREATE_EXAM)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this functionallity on classRoom"})
        #---------------
        privileges = currentClassRoom.Privileges.all()
        adminPrivileges = [priv for priv in privileges if priv.Privilege & UserPrivileges.CREATE_EXAM.value]
        studentsPrivileges = [priv for priv in privileges if priv.Privilege & UserPrivileges.SOLVE_EXAM_ALLOWANCE.value]
        admins = []
        for user in adminPrivileges:
            admins += list(user.Users.all())
        #---------------
        students = []
        for user in studentsPrivileges:
            students += list(user.Users.all())
        #---------------
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
        #---------------
        Committe.objects.bulk_create(committes)
        allCommittesLists = []
        for i,committe in enumerate(committes):
            start = i * CommitteStudentsCount
            end = start + CommitteStudentsCount - 1
            allCommittesLists += [CommitteAllowedList(users=st,committe=committe,present=False) for st in students[start:end]]
        #---------------
        CommitteAllowedList.objects.bulk_create(allCommittesLists)
    #---------------
    def ManualcreateCommitee(self,currentClassRoom:classRoom,Exam:Exam,admins:list[IUserHelper]):
        if not self._checkForPrivilege(currentClassRoom,UserPrivileges.CREATE_EXAM)["isSuccess"]:
            return GOutput(error={"unauthorized":"cannot access this functionallity on classRoom"})
        #---------------
        privileges = currentClassRoom.Privileges.all()
        studentsPrivileges = [priv for priv in privileges if priv.Privilege & UserPrivileges.SOLVE_EXAM_ALLOWANCE.value]
        students = []
        for user in studentsPrivileges:
            students += list(user.Users.all())
        #---------------
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
        #---------------
        Committe.objects.bulk_create(committes)
        allCommittesLists = []
        for i,committe in enumerate(committes):
            start = i * CommitteStudentsCount
            end = start + CommitteStudentsCount - 1
            allCommittesLists += [CommitteAllowedList(users=st,committe=committe,present=False) for st in students[start:end]]
        #---------------
        CommitteAllowedList.objects.bulk_create(allCommittesLists)
    #---------------
#---------------CLASS_ENDED#---------------