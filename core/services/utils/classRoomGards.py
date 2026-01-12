from enum import IntEnum, StrEnum
from typing import Any
from core.models.Exams_models import Privileges, classRoom
from core.services.types.questionType import GeneralOutput
from core.services.types.userType import IUserHelper
from core.services.utils.generalOutputHelper import GOutput


class GardAttribute(IntEnum):
    CREATE_EXAM= "allowCreateExam"
    DELETE_EXAM= "allowDeleteExam"
    CHANGE_EXAM= "allowUpdateExam"
    SEE_EXAM= "allowAccessExam"
    SEE_STUDENTS_SOLN= "allowAccessSolnSheet"
    CORRECTING_STUDENTS_SOLN= "allowCorrectingSolnSheet"
    PANNING_STUDENTS= "allowBanningSolnSheet"
    SOLVE_EXAM_ALLOWANCE= "allowCreatingSolnSheet"
    CREATE_STUDENTS_ACCOUNT= "allowCreateStudentAccount"
    ADD_STUDENTS= "allowAddStudentsAccount"
    LIST_STUDENTS= "allowListStudentsAccounts"
    REMOVE_STUDNET= "allowRemoveStudentAccount"
    ACCESS_CLASSROOM_WITHOUT_PAYING= "allowAccessWithoutPayment"
    ACCESS_ATTACHMENT_WITHOUT_PAYING= "allowAcceessAttachemtsWithoutPayment"
    ACCESS_CHATROOM_WITHOUT_PAYING= "allowAccessChatRoomWithoutPayment"
#------------------


def ClassRoomGard(attribute:GardAttribute):
    def decorator(func):
        def wrapper(self,Requester:IUserHelper,classRoom:classRoom,*args,**kwargs)->GeneralOutput:
            if Requester == classRoom.OwnedBy:
                return func(self,Requester,classRoom,*args,**kwargs)
            RequesterPrivileges = Requester.Privileges.filter(classRoom=classRoom).first()
            if not RequesterPrivileges:
                return GOutput(error={"unauthorized":"cannot access this resource"})
            if RequesterPrivileges.__getattribute__(attribute.value):
                return func(self,Requester,classRoom,*args,**kwargs)
            else:
                paidClassRoom = Requester.Payment_classRoom.filter(classRoom=classRoom).first()
                if paidClassRoom:
                    return func(self,Requester,classRoom,*args,**kwargs)
                #------------------
            #------------------
            return GOutput(error={"unauthorized":"cannot access this resource"})
        #------------------
        return wrapper
    #------------------
    return decorator
#------------------