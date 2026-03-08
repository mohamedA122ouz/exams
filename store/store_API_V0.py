from django.http import HttpRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def UsershowItems(request:HttpRequest,storeName:str):
    ...
#---------------
@api_view(['GET'])
def UserfeedPage(request:HttpRequest):
    ...
#---------------
@api_view(['GET'])
def UserShowItemDetials(request:HttpRequest):
    ...
#---------------
@api_view(['GET'])
def UserAddToCart(request:HttpRequest):
    ...
#---------------
@api_view(['GET'])
def UserCheckOut(request:HttpRequest):
    ...
#---------------
@api_view(['GET'])
def AdminViewRequest(request:HttpRequest):
    ...
#---------------
@api_view(['POST'])
def AdminChangeStateToProgress(request:HttpRequest):
    ...
#---------------
@api_view(['POST'])
def AdminAssignDeliveryPerson(request:HttpRequest):
    ...
#---------------
@api_view(['POST'])
def DeliveryAcceptPackage(request:HttpRequest):
    ...
#---------------
@api_view(['GET'])
def DeliveryShowOwnerCredentials(request:HttpRequest):
    ...
#---------------
@api_view(['POST'])# need to check the phone location
def DeliveryState(request:HttpRequest):
    # he can submit it is delivered or owner is not found - to allow re-schedular
    ...
#---------------
@api_view(['POST'])
def OwnerVerifyRecieve(request:HttpRequest):
    #Optional it will automatically verified after 24h of DeliveryState is delivered
    ...
#---------------
@api_view(['POST'])
def OwnerReview(request:HttpRequest):
    ...
#---------------


