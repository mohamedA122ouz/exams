from typing import cast
from core.models.Exams_models import classRoom
from core.services.types.questionType import GeneralOutput
from core.services.types.userType import IUserHelper
from core.services.utils.generalOutputHelper import GOutput
from core.services.utils.priviliages import UserPrivileges


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
    def _addClassRoomSettings(self):
        # paymentAmount
        # PaymentExpireInterval_MIN
        # PaymentAccessMaxCount
        # ID
        # OwnedBy
        # Teacher
        # Students
        # Admin
        # Attachments
        # HideFromSearch
        # Exams
        ...
    #------------------
    def createClassRoom(self,title:str):
        ...