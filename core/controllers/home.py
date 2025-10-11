from typing import Any
from django.http import HttpRequest, HttpResponse,JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET,require_POST
from core.models.Exams_models import Exam, Subject
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate
from django.views.decorators.csrf import csrf_exempt

def home(request:HttpRequest):
    return render(request,"home/home.html")

@require_POST
@csrf_exempt
def createUser(request:HttpRequest):
    username = request.POST.get("username",None)
    password = request.POST.get("password",None)
    password2 = request.POST.get("password2",None)
    email = request.POST.get("email",None)
    lastName = request.POST.get("lastname",None)
    firstName = request.POST.get("firstname",None)
    errorDict:dict[str,Any] = {}
    if username == None:
        errorDict["username"] = "is Null"
    if password == None :
        errorDict["password"] = "is Null"
    if email == None :
        errorDict["email"] = "is Null"
    if lastName == None :
        errorDict["lastName"] = "is Null"
    if firstName == None :
        errorDict["firstName"] = "is Null"
    if password2 == None:
        errorDict["password2"] = "is Null"
    if(password2 != password):
        errorDict["password2"] = "is different the entered password"
    if len(errorDict) != 0:
        return JsonResponse(errorDict)
    
    try:
        user = User.objects.create_user(username=username,password=password,email=email,last_name=lastName,first_name=firstName)#type:ignore
        if not user:
            return JsonResponse({"signup":"faild"},status=400)
        return JsonResponse({"signup":"successful"})
    except Exception as e:
        message:str = str(e)
        print(message)
        print("Duplicate" in message)
        if("Duplicate" in message and "auth_user.username" in message ):
            return JsonResponse({"signup":"faild already used username"},status=400)
        return JsonResponse({"signup":"faild unknown reason contact admin"},status=400)
        
    
@require_POST
@csrf_exempt
def userLogin(request:HttpRequest):
    username = request.POST.get("username",None)
    password = request.POST.get("password",None)
    if username == None:
        return JsonResponse({"username":"is null"})
    if password == None:
        return JsonResponse({"password":"is null"})
    user = authenticate(request=request,password=password,username=username)
    if not user == None:
        login(request,user)
        return JsonResponse({"login":"successfully done"})
    else:
        return JsonResponse({"login":"faild"})