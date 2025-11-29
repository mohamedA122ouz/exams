from typing import Optional
from django.http import HttpRequest,JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import csrf_exempt
from core.services.questionService import QuestionServices
from core.services.lecutreService import LectureService
from core.services.subjectService import SubjectService
from core.services.termService import TermService
from core.services.jsonResponseHelper import ResponseHelper
from core.services.viewResponseHelper import HTMLResponse
from core.services.yearServices import YearService


@require_GET
def showYears(request:HttpRequest):
    return render(request,"home/home.html",HTMLResponse(YearService().showYears(request.user)))
#------------------
@require_POST
def createYear(request:HttpRequest):
    yearName = request.POST.get("name",None)
    return ResponseHelper(YearService().createYear(request.user,yearName))
#------------------
#level two
@require_GET
@csrf_exempt
def showTerms(request:HttpRequest)->JsonResponse:
    yearID = request.GET.get("year_id",None)
    return ResponseHelper(TermService().showTerms(request.user,yearID))
#------------------
@require_POST
@csrf_exempt
def createTerm(request:HttpRequest):
    termName = request.POST.get("name",None)
    yearID = request.POST.get("year_id",None)
    return ResponseHelper(TermService().createTerm(request.user,termName,yearID))
#level three
@require_GET
@csrf_exempt
def showSubjects(request:HttpRequest):
    return ResponseHelper(SubjectService().showSubjects(request.user))
#------------------
@require_POST
@csrf_exempt
def createSubject(request:HttpRequest):
    yearID = request.POST.get("year_id",None)
    termID = request.POST.get("term_id",None)
    name =request.POST.get("name",None)
    return ResponseHelper(SubjectService().createSubject(request.user,yearID,termID,name))
#------------------
@require_GET
@csrf_exempt
def showLectures(request:HttpRequest)->JsonResponse:
    subjectID = request.GET.get("subject_id",None)
    return ResponseHelper(LectureService().showLectures(request.user,subjectID))
#------------------
@require_POST
@csrf_exempt
def createLectures(request:HttpRequest)->JsonResponse:
    name = request.POST.get("name",None)
    subjectID = request.POST.get("subject_id",None)
    return ResponseHelper(LectureService().createLectures(request.user,name,subjectID))
#------------------
@require_GET
@csrf_exempt
def showQuestions(request:HttpRequest)->JsonResponse:
    lecture = request.GET.get("lecture",None)
    return ResponseHelper(QuestionServices().showQuestions(request.user,lecture))
#------------------
@require_POST
@csrf_exempt
def createQuestion(request:HttpRequest)->JsonResponse:
    Text_Url:Optional[str] = request.POST.get("text_url",None)
    Type:Optional[str|int] = request.POST.get("type",None)
    Ans:Optional[str] = request.POST.get("ans",None)
    lectureID:Optional[str] = request.POST.get("lecture_id",None)
    return ResponseHelper(QuestionServices().createQuestion(request.user,Text_Url,Type,Ans,lectureID))
#------------------
@require_POST
@csrf_exempt
def createQuestions(request:HttpRequest)->JsonResponse:
    questionsNum = request.POST.get("num",None)
    Text_Url:Optional[list[str]] = request.POST.getlist("text_url[]",None)
    Type:Optional[list[str]|list[int]] = request.POST.getlist("type[]",None)
    Ans:Optional[list[str]] = request.POST.getlist("ans[]",None)
    lectureIDs:Optional[list[str]] = request.POST.getlist("lecture_id[]",None)
    return ResponseHelper(QuestionServices().createQuestions(request.user,questionsNum,Text_Url,Type,Ans,lectureIDs))
#------------------