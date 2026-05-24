from typing import Union

from core.models.Exams_models import Profitable
from core.services.types.userType import IUserHelper
from django.db.models import Model



class BaseServiceProvider:
    def __init__(self,Requester:IUserHelper,ModelProvider:Profitable,ProvidedObject:Union[Profitable,int]):
        self.Requester = Requester
        self.ModelProvider = ModelProvider
        if not ModelProvider:
            raise ValueError("model provider cannot be null")
        if not ProvidedObject:
            raise ValueError("provided object cannot be null")
        if isinstance(ProvidedObject,int):
            self.ProvidedObject = ModelProvider.objects.get(id=ProvidedObject)
        else:
            self.ProvidedObject = ProvidedObject
        #------------------
        self.UNAUTHORIZED = {"unauthorized":"cannot access this resource"}
        self.NOT_FOUND = {"not found":"the requested resource is not found"}
        self.FAIL = {"fail":"something went wrong"}
    #------------------
#------------------