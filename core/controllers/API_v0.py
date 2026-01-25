import json
from typing import Optional, cast
from django.http import HttpRequest, HttpResponse,JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import csrf_exempt
import pdfkit
from core.models.Exams_models import Exam, Privileges
from core.services import examService
from core.services.classRoomService import classRoomService
from core.services.questionService import QuestionServices
from core.services.lecutreService import LectureService
from core.services.subjectService import SubjectService
from core.services.termService import TermService
from core.services.types.examTypes import ExamSettings, examRequest
from core.services.types.userType import IUserHelper
from core.services.utils.classRoomTypes import ClassRoomFromFrontend
from core.services.utils.examParser import autoGeneratorParser
from core.services.utils.generalOutputHelper import GOutput
from core.services.utils.jsonResponseHelper import ResponseHelper
from core.services.types.questionType import ExamAutoGenerator, QuestionFromFront, QuestionToFront
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
def createExam(request:HttpRequest)->JsonResponse:
    body:examRequest = cast(examRequest,json.loads(request.body))
    ee = GeneralExamServices(request.user)
    settings = cast(ExamSettings,{})
    if not "title" in body:
        return ResponseHelper({"title":"cannot be null"})
    if not "subject_id" in body:
        return ResponseHelper({"subject_id":"cannot be null"})
    if not "questions" in body:
        return ResponseHelper({"questions":"cannot be null"})
    if not "settings" in body:
        return ResponseHelper({"settings":"cannot be null"})
    settings:ExamSettings = cast(ExamSettings,body["settings"])
    
    output = ee.createExamHybrid(body["title"],body["subject_id"],body["questions"],settings)
    if output["isSuccess"]:
        return ResponseHelper({"success":"exam created successfully"})
    return ResponseHelper(output)
#------------------
@require_GET
@csrf_exempt
def listExams(request:HttpRequest):
    user = cast(IUserHelper,request.user)
    allExams = list(user.Exams.values(
        "Title",
        "ID",
        "CreatedAt",
        "Subject_id",
        "Owner_id",
        "PreventOtherTabs",
        "Duration_min",
        "AutoCorrect",
        "QuestionByQuestion",
        "ShareWith",
        "AllowDownLoad",
        "StartAt",
        "EndAt",
    ))
    return ResponseHelper(allExams)
#------------------
@require_GET
@csrf_exempt
def showExam(request:HttpRequest):
    user = cast(IUserHelper,request.user)
    examID = request.GET.get("exam_id",None)
    if not examID:
        return ResponseHelper({"exam_id":"cannot be null"})
    examService = GeneralExamServices(user)
    exam:Optional[Exam] = user.Exams.filter(ID=examID).first()
    if not exam:
        return ResponseHelper({"exam":"is not exist"})
    frontEndData = examService.sendCredentials(exam)
    return ResponseHelper(frontEndData)
#------------------
@require_GET
@csrf_exempt
def download(request:HttpRequest):
    user = cast(IUserHelper,request.user)
    exam_GEN = GeneralExamServices(user)
    exam = Exam.objects.first()
    if not exam:
        return ResponseHelper(GOutput(error={"test":"testing"}))
    examCre = exam_GEN.sendCredentials(exam,"killer")
    if not examCre["isSuccess"] and not examCre["output"]:
        return ResponseHelper(examCre)
    #------------------
    questions:list[QuestionToFront] = examCre["output"]#type:ignore
    sections:dict[str,list[QuestionToFront]] = {}
    for i,q in enumerate(questions):
        if not q["sectionName"] in sections:
            if not q["sectionName"]:
                q["sectionName"] = ""
            #------------------
            sections[q["sectionName"]] = [q]
            continue
        #------------------
        sections[q["sectionName"]].append(q)
    #------------------
    i = render(request,"printingTemplates/examEN.html",{
        "title":exam.Title,
        "duration":exam.Duration_min,
        "subject":exam.Subject.Name,
        "mark":exam.TotalMark,
        "sections":sections,
        "year":exam.Subject.Year.Name,
        "startAt":exam.StartAt,
    })
    return i
#------------------
@require_POST
@csrf_exempt
def createClassRoom(request:HttpRequest):
    body = cast(ClassRoomFromFrontend,json.loads(request.body))
    user = cast(IUserHelper,request.user)
    clService = classRoomService(user)
    # automatically connect the teacher or the class room owner to the class room live session
    return ResponseHelper(clService.createClassRoom(body))
#------------------
@require_GET
@csrf_exempt
def listclassRooms(request:HttpRequest):
    user = cast(IUserHelper,request.user)
    clService = classRoomService(user)
    return ResponseHelper(clService.listClassRooms())
#------------------

