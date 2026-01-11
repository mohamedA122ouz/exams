from typing import Any, Optional
from core.models.Exams_models import Privileges, classRoom
from core.services.types.userType import IUserHelper


def accessClassRoomGard(func):
    def wrapper(user:IUserHelper,classRoom:classRoom,*args,**kwargs)->Any:
        userPrivileges = user.Privileges.filter(classRoom=classRoom).first()
        if not userPrivileges:
            return None
        if userPrivileges.allowAccessWithoutPayment:
            return func(user,classRoom,*args,**kwargs)
        else:
            paidClassRoom = user.Payment_classRoom.filter(classRoom=classRoom).first()
            if paidClassRoom:
                return func(user,classRoom,*args,**kwargs)
            #------------------
        #------------------
        return None
    #------------------
    return wrapper
#------------------
def accessChatRoomGard(func):
    def wrapper(user:IUserHelper,classRoom:classRoom,*args,**kwargs)->Any:
        userPrivileges = user.Privileges.filter(classRoom=classRoom).first()
        if not userPrivileges:
            return None
        if userPrivileges.allowAccessChatRoomWithoutPayment:
            return func(user,classRoom,*args,**kwargs)
        else:
            paidClassRoom = user.Payment_classRoom.filter(classRoom=classRoom).first()
            if paidClassRoom:
                return func(user,classRoom,*args,**kwargs)
            #------------------
        #------------------
        return None
    #------------------
    return wrapper
#------------------
