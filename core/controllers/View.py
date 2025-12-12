from typing import Optional, cast
from django.http import HttpRequest,JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import csrf_exempt
from core.services.questionService import QuestionServices
from core.services.lecutreService import LectureService
from core.services.subjectService import SubjectService
from core.services.termService import TermService
from core.services.types import userType
from core.services.utils.examParser import autoGeneratorParser
from core.services.utils.jsonResponseHelper import ResponseHelper
from core.services.types.questionType import ExamAutoGenerator
from core.services.utils.viewResponseHelper import HTMLResponse
from core.services.yearServices import YearService


@require_GET
def showYears(request:HttpRequest):
    limit = request.GET.get("limit",100)
    if isinstance(limit,str) and limit.isnumeric():
        limit = int(limit)
    last_id = request.GET.get("last_id",0)
    if isinstance(last_id,str) and last_id.isnumeric():
        last_id = int(last_id)
    return render(request,"home/home.html",HTMLResponse(YearService().showYears(request.user,cast(int,limit),cast(int,last_id))))
#------------------
@require_POST
def createYear(request:HttpRequest):
    yearName = request.POST.get("name",None)
    return ResponseHelper(YearService().createYear(request.user,yearName))
#------------------
@require_GET
@csrf_exempt
def showTerms(request:HttpRequest)->JsonResponse:
    limit = request.GET.get("limit",100)
    if isinstance(limit,str) and limit.isnumeric():
        limit = int(limit)
    last_id = request.GET.get("last_id",0)
    if isinstance(last_id,str) and last_id.isnumeric():
        last_id = int(last_id)
    yearID = request.GET.get("year_id",None)
    return ResponseHelper(TermService().showTerms(request.user,yearID,cast(int,limit),cast(int,last_id)))
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
    limit = request.GET.get("limit",100)
    if isinstance(limit,str) and limit.isnumeric():
        limit = int(limit)
    last_id = request.GET.get("last_id",0)
    if isinstance(last_id,str) and last_id.isnumeric():
        last_id = int(last_id)
    return ResponseHelper(SubjectService().showSubjects(request.user,cast(int,limit),cast(int,last_id)))
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
    limit = request.GET.get("limit",100)
    if isinstance(limit,str) and limit.isnumeric():
        limit = int(limit)
    last_id = request.GET.get("last_id",0)
    if isinstance(last_id,str) and last_id.isnumeric():
        last_id = int(last_id)
    subjectID = request.GET.get("subject_id",None)
    return ResponseHelper(LectureService().showLectures(request.user,subjectID,cast(int,limit),cast(int,last_id)))
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
    limit = request.GET.get("limit",100)
    if isinstance(limit,str) and limit.isnumeric():
        limit = int(limit)
    last_id = request.GET.get("last_id",0)
    if isinstance(last_id,str) and last_id.isnumeric():
        last_id = int(last_id)
    lecture = request.GET.get("lecture_id",None)
    return ResponseHelper(QuestionServices().showQuestions(request.user,lecture,cast(int,limit),cast(int,last_id)))
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



@require_GET
@csrf_exempt
def test(request:HttpRequest)->JsonResponse:
    examStructure:ExamAutoGenerator = {
            'generatorSettings':{
                "lectureName":"lec1",
                'subjectName':"advanced OOP1",
                'randomization':True,
                'termName':'term1',
                'yearName':'Year1'
            },
            'questions':[
                {'count':2,'ease':0},
                {'count':2,'ease':1},
                {'count':2,'ease':2},
            ]
        }
    exam = autoGeneratorParser(examStructure)
    return JsonResponse(exam,safe=False)
#------------------