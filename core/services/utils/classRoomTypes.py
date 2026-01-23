from typing import TypedDict


class ClassRoomFromFrontend(TypedDict):
    title:str
    HideFromSearch:bool
    paymentAmount:float
    PaymentExpireInterval_MIN:int
    PaymentAccessMaxCount:int
#------------------
