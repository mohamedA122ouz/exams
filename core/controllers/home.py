from typing import Any
from django.http import HttpRequest, HttpResponse,JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET,require_POST
from core.models.Exams_models import Exam, Subject
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate
from django.views.decorators.csrf import csrf_exempt

from core.services.utils.jsonResponseHelper import ResponseHelper

def home(request:HttpRequest):
    return render(request,"home/home.html")

def signup(request:HttpRequest):
    return render(request,"registration/signup.html")
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
        errorDict["lastname"] = "is Null"
    if firstName == None :
        errorDict["firstname"] = "is Null"
    if password2 == None:
        errorDict["password2"] = "is Null"
    if(password2 != password):
        errorDict["password2"] = "is different the entered password"
    if len(errorDict) != 0:
        if request.path.startswith("/api/"):
            return ResponseHelper(errorDict)
        return render(request,"utils/faild.html")
    
    try:
        user = User.objects.create_user(username=username,password=password,email=email,last_name=lastName,first_name=firstName)#type:ignore
        if not user:
            if request.path.startswith("/api/"):
                return ResponseHelper({"fail":"something went wrong"})
            return render(request,"utils/faild.html")
        if request.path.startswith("/api/"):
            return ResponseHelper({"success":"signup success"})
        return render(request,"utils/createdSuccessful.html")
    except Exception as e:
        message:str = str(e)
        print(message)
        print("Duplicate" in message)
        if("Duplicate" in message and "auth_user.username" in message ):
            return ResponseHelper({"username":"is already exist"})
        return ResponseHelper({"fail":"unknown reason"})
        

def userloginPage(request:HttpRequest):
    return render(request,"registration/login.html")
@require_POST
@csrf_exempt
def userLogin(request:HttpRequest):
    username = request.POST.get("username",None)
    password = request.POST.get("password",None)
    if username == None:
        return ResponseHelper({"username":"is null"})
    if password == None:
        return ResponseHelper({"password":"is null"})
    user = authenticate(request=request,password=password,username=username)
    if not user == None:
        login(request,user)
        return ResponseHelper({"success":"successfully done"})
    else:
        return ResponseHelper({"login":"username/password is wrong"})