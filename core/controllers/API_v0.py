import json
from typing import Optional
from django.http import HttpRequest,JsonResponse
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import csrf_exempt
from core.services.questionService import QuestionServices
from core.services.lecutreService import LectureService
from core.services.subjectService import SubjectService
from core.services.termService import TermService
from core.services.utils.jsonResponseHelper import ResponseHelper
from core.services.yearServices import YearService

#level one
@require_GET
def showYears(request:HttpRequest):
    return ResponseHelper(YearService().showYears(request.user))
#------------------
@csrf_exempt
@require_POST
def createYear(request:HttpRequest):
    body:dict = json.loads(request.body)
    yearName = body.get("name",None)
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
    body:dict = json.loads(request.body)
    termName = body.get("name",None)
    yearID = body.get("year_id",None)
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
    body:dict = json.loads(request.body)
    yearID = body.get("year_id",None)
    termID = body.get("term_id",None)
    name =body.get("name",None)
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
    body:dict = json.loads(request.body)
    name = body.get("name",None)
    subjectID = body.get("subject_id",None)
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
    body:dict = json.loads(request.body)
    Text_Url:Optional[str] = body.get("text_url",None)
    Type:Optional[str|int] = body.get("type",None)
    Ans:Optional[str] = body.get("ans",None)
    lectureID:Optional[str] = body.get("lecture_id",None)
    return ResponseHelper(QuestionServices().createQuestion(request.user,Text_Url,Type,Ans,lectureID))
#------------------
@require_POST
@csrf_exempt
def createQuestions(request:HttpRequest)->JsonResponse:
    body:dict = json.loads(request.body)
    questionsNum = body.get("num",None)
    Text_Url:Optional[list[str]] = body.get("text_urls",None)
    Type:Optional[list[str]|list[int]] = body.get("types",None)
    Ans:Optional[list[str]] = body.get("ans",None)
    lectureIDs:Optional[list[str]] = body.get("lecture_ids",None)
    return ResponseHelper(QuestionServices().createQuestions(request.user,questionsNum,Text_Url,Type,Ans,lectureIDs))
#------------------