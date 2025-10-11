from typing import Literal, Optional
from django.contrib.auth.models import User
from core.models.Exams_models import Subject, Year,Term
from django.http import HttpRequest, JsonResponse

class YearHttpRequest(HttpRequest):
    year = Optional["Year"]
#---------------
def yearAuthLogic(request:HttpRequest,funcType:Literal["GET","POST"])->dict[str,bool]:
    userID = request.user#type:ignore
    yearID = None
    if funcType == 'GET':
        yearID = request.GET.get("yearID")
    elif funcType == 'POST':
        yearID = request.POST.get("yearID")
    if not userID:
        return {"user":False}
    if not yearID:
        return {"yearID":False}
    year:Optional["Year"] = Year.objects.filter(User_id=userID,id=yearID).first()
    if year:
        request.year = year #type:ignore
        return {"year":True}
    return {"year":False}
#---------------
def authYear(methodType:Literal['GET','POST']):
    def decorator(func):
        def wrapper(request:HttpRequest,*args,**kwargs):
            yearObj = yearAuthLogic(request,methodType)
            if ('year' in yearObj) and yearObj["year"]:
                return func(request,*args,**kwargs)
            else:
                return JsonResponse({"year":"unauthorized access"},status=403)
        return wrapper
    return decorator
#________Year Finished________

class TermHttpRequest(YearHttpRequest):
    term = Optional["Term"]
#----------------
def termsAuthLogic(request:HttpRequest,funcType:Literal['GET','POST'])->dict[str,bool]:
    yearObj:dict[str,bool]= yearAuthLogic(request,funcType)
    if not ("year" in yearObj):
        return yearObj
    if not yearObj["year"]:
        return yearObj
    term:Optional["Term"] = Term.objects.filter(Year_id = request.year.id)#type:ignore
    if not term:
        yearObj["term"] = False
    request[term] = term #type:ignore
    return yearObj
#----------------
def authTerms(methodType:Literal['GET','POST']):
    def decorator(func):
        def wrapper(request:HttpRequest,*args,**kwargs)->JsonResponse:
            authObj:dict[str,bool] = termsAuthLogic(request,methodType)
            errorObj:dict[str,str] = {}
            for item in authObj:
                if not authObj[item]:
                    errorObj[item] = "unauthorized access"
            #-------
            if len(errorObj) == 0:
                return func(request,*args,**kwargs)
            else:
                return JsonResponse(errorObj,status=403)
        #-----------
        return wrapper
    #------------
    return decorator
#----------------
# def subjectAuthLogic(request:HttpRequest)->dict[str,bool]:
#     subjectObj:dict[str,bool] = termsAuthLogic(request)
#     if term in subjectObj
# #----------------

# #_________________
# def authSubject(func):
#     def wrapper(request:HttpRequest):
#         return JsonResponse({},status=403)
#     #---------
#     return wrapper
# #-------------
# def authQBank(func):
#     ...