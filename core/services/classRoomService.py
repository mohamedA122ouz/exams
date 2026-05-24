from datetime import datetime
from math import ceil
from tabnanny import check
from typing import Literal, Optional, Self, Type, Union, cast
from core.models.Exams_models import AttachmentLicence, ClassRoomAttachment, Committe, CommitteAllowedList, Exam, Payment_Attachment, Payment_classRoom, Privileges, WatchHistory, chatRoom, classRoom, classRoom_ClassRoomAttachment, dependenciesRepo, shareWithLink
from core.services.ServiceProviders import BaseServiceProvider
from core.services.types.questionType import GeneralOutput
from core.services.types.userType import IUserHelper
from core.services.utils.classRoomTypes import ClassRoomFromFrontend_TD, ClassRoomFromFrontend_s
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
from functools import wraps

ALLOWED_PAYMENT_PRIVILEGES = Literal[    
                    UserPrivileges.ACCESS_CLASSROOM_WITHOUT_PAYING,
                    UserPrivileges.ACCESS_ATTACHMENT_WITHOUT_PAYING,
                    UserPrivileges.ACCESS_CHATROOM_WITHOUT_PAYING,
                    UserPrivileges._ACCESS_PAID_FOR_FREE
                ]
            


def checkForPrivilege(privilege:UserPrivileges,isExact=False):
    """
    This function without isExact=False "which is the default" check if the user have one or more privileges overlaps ,
    But if isExact=True check if it which is importatn for some causes where you only need specific privilege to access the classroom

    if privilege is UserPrivileges._OWNER_PRIVILEGES and isExact=False it will allow any user to do anything is just like if you don't have any so it will raise an error
    """
    if privilege == UserPrivileges._OWNER_PRIVILEGES and isExact == False:
        raise Exception("cannot use this function with owner privileges without isExact=True")
    def decorator(func):
        @wraps(func)
        def innerWrapper(self:"BaseServiceProvider",*args,**kwargs):
            if not issubclass(type(self),BaseServiceProvider):
                raise TypeError("this decorator can only be used on methods of BaseServiceProvider or its subclasses")
            #------------------
            if self.Requester == self.ProvidedObject.OwnedBy:
                return func(*args,**kwargs)
            #------------------
            wantedClassRoom:classRoom = cast(classRoom,self.ProvidedObject)
            userprivilege = self.Requester.Privileges.filter(ClassRooms=wantedClassRoom).all()
            userprivilege = [priv 
                                for priv in userprivilege
                                    if (priv.Privilege & privilege != 0)
                                        if not isExact or (privilege == priv.Privilege)
                            ]
            if len(userprivilege) > 0:
                return func(*args,**kwargs)
            return GOutput(error=self.UNAUTHORIZED)
        #------------------
        return innerWrapper
    #------------------
    return decorator
#---------------
def checkForPayment(privilege:Optional[ALLOWED_PAYMENT_PRIVILEGES]=None):
    if privilege is not None and privilege not in [    
                    UserPrivileges.ACCESS_CLASSROOM_WITHOUT_PAYING,
                    UserPrivileges.ACCESS_ATTACHMENT_WITHOUT_PAYING,
                    UserPrivileges.ACCESS_CHATROOM_WITHOUT_PAYING,
                    UserPrivileges._ACCESS_PAID_FOR_FREE
                ]:
        raise ValueError("Invalid payment privilege")
    #------------------
    def decorator(func):
        @wraps(func)
        def innerWrapper(self:"BaseServiceProvider",*args,**kwargs):
            if self.Requester == self.ProvidedObject.OwnedBy:
                return func(*args,**kwargs)
            #------------------
            canAccessForFree = False
            def checkFreeAccess(self,*args,**kwargs):
                nonlocal canAccessForFree
                canAccessForFree = True
            #------------------
            checkForPrivilege(privilege=cast(UserPrivileges,privilege))(checkFreeAccess)(self,*args,**kwargs)
            if canAccessForFree:
                return func(*args,**kwargs)
            #------------------
            wantedClassRoom:classRoom = cast(classRoom,self.ProvidedObject)
            if self.Requester == self.ProvidedObject.OwnedBy or wantedClassRoom.paymentAmount == 0 or self.Requester.Privileges.filter(ClassRooms=wantedClassRoom,Privilege=UserPrivileges._OWNER_PRIVILEGES.value).exists():
                return func(*args,**kwargs)
            payment = Payment_classRoom.objects.filter(Owner=self.Requester,Privilege__ClassRooms=wantedClassRoom).order_by('TransactionTime').first()
            if not payment:
                return GOutput(error=self.UNAUTHORIZED)
            if payment.ExpireDateTime.replace(tzinfo=None) >= datetime.now() and payment.Amount == wantedClassRoom.paymentAmount:
                return func(*args,**kwargs)
            if not payment.ExpireDateTime.replace(tzinfo=None) and payment.AccessCounter > 0:
                payment.AccessCounter -= 1
                payment.save()
                return func(*args,**kwargs)
            return GOutput(error=self.UNAUTHORIZED)
        #------------------
        return innerWrapper
    #------------------
    return decorator
#------------------

class classRoomService(BaseServiceProvider):
    def __init__(self,user,classRoom) -> None:
        super().__init__(Requester=cast(IUserHelper,user),ModelProvider=classRoom,ProvidedObject=classRoom)
    #---------------
        # Security_Layer1
    def _UserExists(self,class_room:classRoom)->bool:
        allPrivileges = class_room.Privileges.all()
        users = [p.Users for p in allPrivileges]
        return self.Requester in users
    #---------------
    @checkForPrivilege(privilege=UserPrivileges._OWNER_PRIVILEGES,isExact=True)
    def PrivilegeDetials(self,privilege_ID:int):
        model = Privileges.objects.filter(id=privilege_ID).first()
        serializer = GETREQ_Privileges(model)
        data:GETREQ_Privileges_TYPE = serializer.data #type:ignore
        allPrivileges = UserPrivileges.tojson()
        privileges:list[str] = [ pri for pri in allPrivileges if allPrivileges[pri] & data["Privilege"] != 0]
        return GOutput(privileges)
    #---------------
    @checkForPrivilege(privilege=UserPrivileges._OWNER_PRIVILEGES,isExact=True)
    def editSettings(self,body:ClassRoomFromFrontend_TD)->GeneralOutput:
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
        if not body:
            return GOutput(error=self.FAIL)
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
    @classmethod
    @transaction.atomic
    def createClassRoom(cls,user:IUserHelper,body:ClassRoomFromFrontend_TD)->GeneralOutput:
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
            OwnedBy=user,
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
    @checkForPrivilege(privilege=UserPrivileges._OWNER_PRIVILEGES,isExact=True)
    def defineRoles(self,roleTitle,privileges:UserPrivileges)->GeneralOutput:
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
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
    @checkForPrivilege(privilege=UserPrivileges.ADD_STUDENTS)
    def addUsers(self, role:Privileges,users:list[IUserHelper])->GeneralOutput:
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
        if not currentRoom.Privileges.contains(role):
            return GOutput(error={"privileges":"cannot add user with a not exist privileges"})
        #---------------
        # role.Users.add(cast(User,user))
        role.Users.add(*cast(list[User],users))
        return GOutput({"success":"user created with specified role successfully"})
    #---------------
    @checkForPrivilege(privilege=UserPrivileges.ADD_STUDENTS | UserPrivileges.REMOVE_STUDNET)
    def showUsers(self):
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
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
    @checkForPrivilege(privilege=UserPrivileges.REMOVE_STUDNET,isExact=True)
    def removeUsers(self,role:Privileges,users:list[IUserHelper]):
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
        if not currentRoom.Privileges.contains(role):
            return GOutput(error={"privileges":"cannot remove user with a not exist privileges"})
        #---------------
        role.Users.remove(*cast(list[User],users))
    #---------------
    def addExam(self,Exam:Exam):
        if not Exam:
            return GOutput(error={"Exam":"cannot be null"})
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
        currentRoom.Exams.add(Exam)
    #---------------
    @checkForPrivilege(privilege=UserPrivileges.DELETE_EXAM)
    def removeExam(self,Exam:Exam):
        if not Exam:
            return GOutput(error={"Exam":"cannot be null"})
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
        currentRoom.Exams.remove(Exam)
    #---------------
    @checkForPrivilege(privilege=UserPrivileges.UPLOAD_ATTACHMENT)
    def addAttachment(self,file:InMemoryUploadedFile,paymentAmount:float=0,PaymentExpireInterval_MIN:int=0,PaymentAccessMaxCount:int=0)->GeneralOutput:
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
        mimeFile = magic.from_buffer(file.read(2048),mime=True) 
        file.seek(0)
        if not mimeFile in ALLOWED_MIME_TYPES:
            return GOutput(error={"unauthorized":"cannot upload this type of attachments"})
        hasher = hashlib.sha256()
        for chunk in file.chunks(8192):
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
    @classmethod
    def listClassRooms(cls,user:IUserHelper,limit:int=100,last_id:int=0)->GeneralOutput:
        classRooms = user.Owned_classRooms.order_by('ID').filter(ID__gt=last_id)[:limit].values('ID','Title','HideFromSearch','OwnedBy','paymentAmount','PaymentExpireInterval_MIN','PaymentAccessMaxCount')
        return GOutput(list(classRooms))
    #---------------
    @classmethod
    def listChatRooms(cls,user:IUserHelper,limit:int=100,last_id:int=0)->GeneralOutput:
        # allPrivileges = self.Requester.Privileges.all()
        # classRooms = [privilege.ClassRooms for privilege in allPrivileges]
        # chatRooms = chatRoom.objects.filter(classRoom__in=classRooms).order_by('ID').filter(ID__gt=last_id)[:limit].values('ID','Name','paymentAmount','PaymentExpireInterval_MIN','PaymentAccessMaxCount')
        chatRooms = user.chatRooms.order_by('id').filter(id__gt=last_id)[:limit].values('id','Name','paymentAmount','PaymentExpireInterval_MIN','PaymentAccessMaxCount')
        return GOutput(list(chatRooms))
    #------------------
    @classmethod
    def subscripedClassRooms(cls,user:IUserHelper,limit:int=100,last_id:int=0)->GeneralOutput:
        allPrivileges = user.Privileges.all()
        classRooms = [privilege.ClassRooms for privilege in allPrivileges]
        viewClassRooms = View_ShowClassRoom(classRooms,many=True)
        return GOutput(viewClassRooms.data)
    #---------------
    @checkForPrivilege(privilege=UserPrivileges.LIST_STUDENTS)
    def listUsersWithPrivileges(self,privilege:Privileges,limit:int=100,last_id:int=0):
        return GOutput(list(privilege.Users.values('id',"username",'first_name','last_name','email')))
    #---------------
    @checkForPrivilege(privilege=UserPrivileges._OWNER_PRIVILEGES,isExact=True)
    def listPrivileges(self)->GeneralOutput:
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
        return GOutput(list(currentRoom.Privileges.values('Name','id')))
    #---------------
    @checkForPrivilege(privilege=UserPrivileges.SOLVE_EXAM_ALLOWANCE|UserPrivileges.ACCESS_CLASSROOM_WITHOUT_PAYING)
    @checkForPayment(privilege=UserPrivileges.ACCESS_CLASSROOM_WITHOUT_PAYING)
    def listAttachments(self)->GeneralOutput:
        wantedClassRoom:classRoom = author_Output["output"] #type:ignore
        return GOutput(list(wantedClassRoom.Attachments.values('name','ID')))
    #---------------
    @checkForPayment(privilege=UserPrivileges.ACCESS_CLASSROOM_WITHOUT_PAYING)
    def showAttahcment(self,AttahcmentID:int):
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
        cl_att = currentRoom.Attachments.filter(ID=AttahcmentID).first()
        isVerified = False
        if not cl_att:
            return GOutput(error={"attachment":"not found"})
        if not cl_att.isOrdered or cl_att.order == 1:
            isVerified = True
        #---------------
        history = self.Requester.attachmentHistory.filter(attachment__order__lte=cl_att.order,attachment__classRoom=currentRoom)
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
    @checkForPrivilege(privilege=UserPrivileges.CREATE_EXAM)
    def AutocreateCommitee(self,Exam:Exam):
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
        privileges = currentRoom.Privileges.all()
        adminPrivileges = [priv for priv in privileges if priv.Privilege & UserPrivileges.SEE_STUDENTS_SOLN.value]
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
                clRoom = currentRoom,
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
    @checkForPrivilege(privilege=UserPrivileges.CREATE_EXAM)
    def halfAutomaticCreateCommitee(self,Exam:Exam,admins:list[IUserHelper]):
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
        privileges = currentRoom.Privileges.all()
        studentsPrivileges = [priv for priv in privileges if priv.Privilege & UserPrivileges.SOLVE_EXAM_ALLOWANCE.value]
        students = []
        for user in studentsPrivileges:
            students += list(user.Users.all())
        #---------------
        adminsCount = len(admins)
        studentsCount = len(students)
        CommitteStudentsCount = ceil(studentsCount/adminsCount)
        committes:list[Committe] = [
            Committe(
                clRoom = currentRoom,
                Exam = Exam,
                isOpened = False,
                inspector = admin
            )
            for admin in admins
        ]
        Committe.objects.bulk_create(committes)
        allCommittesLists = []
        allCommittesLists = [
            CommitteAllowedList(users=st,committe=committe,present=False)
            for i,committe in enumerate(committes)
            for st in students[(i * CommitteStudentsCount):((i * CommitteStudentsCount) + CommitteStudentsCount)]
        ]
        CommitteAllowedList.objects.bulk_create(allCommittesLists)
        GOutput({"success":"committee created successfully"})
    #---------------
    @checkForPrivilege(privilege=UserPrivileges.CREATE_EXAM)
    def manualCreateCommittee(self,Exam:Exam,admins:list[IUserHelper],studentsLists:list[list[IUserHelper]]):
        if len(admins) != len(studentsLists):
            return GOutput(error={"admins,students":"must have the same length"})
        #------------------
        currentRoom:classRoom = cast(classRoom,self.ProvidedObject)
        committes:list[Committe] = [
            Committe(
                clRoom = currentRoom,
                Exam = Exam,
                isOpened = False,
                inspector = admin
            )
            for admin in admins
        ]
        Committe.objects.bulk_create(committes)
        allCommitteesLists = [
            CommitteAllowedList(
                users=stList,
                committe=committes[i],
                present=False
            )
            for i,stList in enumerate(studentsLists)
        ]
        CommitteAllowedList.objects.bulk_create(allCommitteesLists)
        GOutput({"success":"committee created successfully"})
    #---------------
#---------------CLASS_ENDED#---------------