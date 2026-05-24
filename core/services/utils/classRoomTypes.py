from typing import TypedDict
from rest_framework import serializers
from core.models.Exams_models import classRoom


class ClassRoomFromFrontend_TD(TypedDict):
    title:str
    HideFromSearch:bool
    paymentAmount:float
    PaymentExpireInterval_MIN:int
    PaymentAccessMaxCount:int
#---------------
class ClassRoomFromFrontend_s(serializers.ModelSerializer):
    class Meta: #type:ignore
        model = classRoom
        fields = "__all__"
#---------------