import json
from typing import Optional, cast
from django.http import HttpRequest,JsonResponse
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import csrf_exempt
from core.services import examService
from core.services.questionService import QuestionServices
from core.services.lecutreService import LectureService
from core.services.subjectService import SubjectService
from core.services.termService import TermService
from core.services.types.examTypes import ExamSettings, examRequest
from core.services.types.userType import IUserHelper
from core.services.utils.examParser import autoGeneratorParser
from core.services.utils.jsonResponseHelper import ResponseHelper
from core.services.types.questionType import ExamAutoGenerator, QuestionFromFront
from core.services.yearServices import YearService
from core.services.examService import GeneralExamServices

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
    lecture = request.GET.get("lecture_id",None)
    return ResponseHelper(QuestionServices(request.user).showQuestions(lecture))
#------------------
@require_POST
@csrf_exempt
def createQuestion(request:HttpRequest)->JsonResponse:
    editor:QuestionFromFront = json.loads(request.body)
    return ResponseHelper(QuestionServices(request.user).createQuestion(editor))
#------------------
@require_POST
@csrf_exempt
def createQuestions(request:HttpRequest)->JsonResponse:
    body:dict = json.loads(request.body)
    editor_input:Optional[list[QuestionFromFront]] = body.get("editor_input",None)
    return ResponseHelper(QuestionServices(request.user).createQuestions(editor_input))
#------------------
@require_POST
@csrf_exempt
def createExam(request:HttpRequest)->JsonResponse:
    body:examRequest = cast(examRequest,json.loads(request.body))
    e = GeneralExamServices(request.user)
    settings = cast(ExamSettings,{})
    if not "title" in body:
        return ResponseHelper({"title":"cannot be null"})
    if not "subject_id" in body:
        return ResponseHelper({"subject_id":"cannot be null"})
    if not "question_ids" in body:
        return ResponseHelper({"question_ids":"cannot be null"})
    if not "settings" in body:
        return ResponseHelper({"settings":"cannot be null"})
    settings:ExamSettings = cast(ExamSettings,body["settings"])
    output = e._manualPickQuestion(body["title"],body["subject_id"],body["question_ids"],settings)
    if output["isSuccess"]:
        return ResponseHelper({"success":"exam created successfully"})
    return ResponseHelper(output)
#------------------
