
import json
from typing import Optional, cast
from django.http import HttpRequest,HttpResponse,JsonResponse
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import csrf_exempt
from core.services.userHelper import IUserHelper

#level one
@require_GET
def showYears(request:HttpRequest):
    user = cast(IUserHelper,request.user)
    years = user.Years.values()
    return JsonResponse(list(years),safe=False)
#------------------
@csrf_exempt
@require_POST
def createYear(request:HttpRequest):
    yearName = request.POST.get("name")
    if yearName == None:
        return JsonResponse({"name":"cannot be null"})
    tempUser = cast(IUserHelper,request.user)
    if tempUser.Years.filter(Name=yearName).exists():
        return JsonResponse({"name":"cannot create two years with the same name"})
    year = tempUser.Years.create(Name=yearName)
    if year:
        return JsonResponse({"year":"created successfully"})
#------------------
#level two
@require_GET
@csrf_exempt
def showTerms(request:HttpRequest)->JsonResponse:
    user = cast(IUserHelper,request.user)
    yearID = request.GET.get("year_id",None)
    if not yearID:
        return JsonResponse({"terms":"year is not specified"})
    terms = user.Terms.filter(Year__ID=yearID).values()
    return JsonResponse(list(terms),safe=False)
#------------------
@require_POST
@csrf_exempt
def createTerm(request:HttpRequest):
    termName = request.POST.get("name",None)
    yearID = request.POST.get("year_id",None)
    if not (termName):
        return JsonResponse({"name":"term name is null"},status=400)
    if not yearID:
        return JsonResponse({"name":"year ID cannot be null"},status=400)
    user = cast(IUserHelper,request.user)
    year = user.Years.filter(ID=yearID).first()
    if not year:
        return JsonResponse({"name":"year doesn't exist"},status=400)
    term = user.Terms.create(Year=year,Name=termName)
    if term:
        return JsonResponse({"creation":"Term Created Successfully"})
    return JsonResponse({"creation":"term creation faild"})
#level three
@require_GET
@csrf_exempt
def showSubjects(request:HttpRequest): 
    # I need to authorize person and show the subject for this person and for this subject only
    # Subject.objects.filter()
    user = cast(IUserHelper,request.user)
    if not user:
        return JsonResponse({"subjects":"required login"})
    subjects = user.Subjects.values()
    return JsonResponse(list(subjects),safe=False)
#------------------
@require_POST
@csrf_exempt
def createSubject(request:HttpRequest):
    user = cast(IUserHelper,request.user)
    yearID = request.POST.get("year_id",None)
    termID = request.POST.get("term_id",None)
    name =request.POST.get("name",None)
    if not termID:
        return JsonResponse({"term_id":"term Id cannot be null"})
    if not yearID:
        return JsonResponse({"year_id":"cannot year ID be null"})
    if not name:
        return JsonResponse({"name":"cannot give null name"})
    term = user.Terms.filter(ID=termID).first()
    if not term:
        return JsonResponse({"creation":"faild term is not exist"})
    year = user.Years.filter(ID=yearID).first()
    if not year:
        return JsonResponse({"creation":"faild year is not exist"})
    subject = user.Subjects.create(
        Name=name,
        Year=year,
        Term=term
    )
    if not subject:
        return JsonResponse({"creation":"faild no reason specified"})
    return JsonResponse({"creation":"successful"})
#------------------
@require_GET
@csrf_exempt
def showLectures(request:HttpRequest)->JsonResponse:
    user = cast(IUserHelper,request.user)
    subjectID = request.GET.get("subject_id",None)
    if not subjectID:
        return JsonResponse({"subject":"subject cannot be null"})
    lecture = user.Lectures.filter(Subject__ID=subjectID).values()
    if not lecture:
        return JsonResponse({"lecture":"no lecture found"})
    return JsonResponse(list(lecture),safe=False)
#------------------
@require_POST
@csrf_exempt
def createLectures(request:HttpRequest)->JsonResponse:
    user = cast(IUserHelper,request.user)
    name = request.POST.get("name",None)
    subjectID = request.POST.get("subject_id",None)
    if not name:
        return JsonResponse({"name":"cannot give null name"})
    if not subjectID:
        return JsonResponse({"subject_id":"cannot be null"})
    subject = user.Subjects.filter(ID=subjectID).first()
    if not subject:
        return JsonResponse({"subject":"is not found"})
    lecture = user.Lectures.create(
        Name=name,
        Subject=subject
    )
    if not lecture:
        return JsonResponse({"lecture":"no lecture created"})
    return JsonResponse({"creation":"successful"})
#------------------
def createQuestion(request:HttpRequest)->JsonResponse:
    user = cast(IUserHelper,request.user)
    Text_Url:Optional[str] = request.POST.get("text_url",None)
    Type:Optional[str|int] = request.POST.get("type",None)
    Ans:Optional[str] = request.POST.get("ans",None)
    lectureID:Optional[str] = request.POST.get("lecture_id",None)
    if not Text_Url:
        return JsonResponse({"Text_Url":"cannot be null"})
    if not Type:
        return JsonResponse({"Type":"cannot be null"})
    if not Ans:
        return JsonResponse({"Ans":"cannot be null"})
    if not lectureID:
        return JsonResponse({"lectureID":"cannot be null"})
    lecture = user.Lectures.filter(ID=lectureID).first()
    if not lecture:
        return JsonResponse({"lecture":"lecture not found"})
    if not Type.isnumeric():
        return JsonResponse({"type":"must be number"})
    elif Type.isnumeric():
        Type = int(Type)
        if Type >= 3:
            Type = 2
    #------------------
    q = user.Questions.create(
        Text_Url=Text_Url,
        Type=int(Type),
        Ans=Ans,
        IsInAnExam = False,
        soln=None
    )
    if not q:
        return JsonResponse({"creation":"faild"})
    return JsonResponse({"creation":"Successful"})