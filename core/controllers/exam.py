import json
from os import name
from django.http import HttpRequest,HttpResponse,JsonResponse
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import csrf_exempt
from core.models.Exams_models import Term, Year
from core.services.authorizeAccess import YearHttpRequest, authYear

#level one
@require_GET
def showYears(request:YearHttpRequest):
    years = Year.objects.filter(User_id=request.user.id).values() #type:ignore
    return JsonResponse(list(years),safe=False)
@csrf_exempt
@require_POST
def createYear(request:HttpRequest):
    yearName = request.POST.get("name")
    userID = request.user.id #type:ignore
    if yearName == None:
        return JsonResponse({"name":"cannot be null"})
    year = Year.objects.create(Name=yearName,User_id=userID)
    if year:
        return JsonResponse({"year":"created successfully"})

#level two
@require_GET
@csrf_exempt
@authYear('GET')
def showTerms(request:YearHttpRequest)->JsonResponse:
    terms = request.year.Terms.values() #type:ignore
    return JsonResponse(list(terms),safe=False)
@require_POST
@csrf_exempt
@authYear('POST')
def createTerm(request:YearHttpRequest):
    termName = request.POST.get("name",None)
    if not (termName):
        return JsonResponse({"name":"term name is null"},status=400)
    Term.objects.create(Name=termName,Year_id=request.year.id) #type:ignore
    return JsonResponse({"success":"Term Create Successfully"})

#level three
def showSubjects(request:HttpRequest):
    ...
def createSubject(request:HttpRequest):
    ...