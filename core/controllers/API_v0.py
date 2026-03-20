import json
from typing import Optional, cast
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import csrf_exempt
from core.models.Exams_models import Committe, Exam, classRoom
from core.services.classRoomService import classRoomService
from core.services.committeService import CommitteServices
from core.services.questionService import QuestionServices
from core.services.lectureService import LectureService
from core.services.subjectService import SubjectService
from core.services.termService import TermService
from core.services.types.examTypes import ExamSettings, Location_Type, examRequest
from core.services.types.userType import IUserHelper
from core.services.utils.classRoomTypes import ClassRoomFromFrontend
from core.services.utils.generalOutputHelper import GOutput
from core.services.utils.jsonResponseHelper import ResponseHelper
from core.services.types.questionType import QuestionFromFront, QuestionToFront
from core.services.utils.priviliages import UserPrivileges
from core.services.yearServices import YearService
from core.services.examService import GeneralExamServices
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.models import User
from rest_framework.decorators import api_view

#level one
@require_GET
def showYears(request:HttpRequest):
    return ResponseHelper(YearService().showYears(request.user))
#---------------
@csrf_exempt
@require_POST
def createYear(request:HttpRequest):
    body:dict = json.loads(request.body)
    yearName = body.get("name",None)
    return ResponseHelper(YearService().createYear(request.user,yearName))
#---------------
#level two
@require_GET
@csrf_exempt
def showTerms(request:HttpRequest)->JsonResponse:
    yearID = request.GET.get("year_id",None)
    return ResponseHelper(TermService().showTerms(request.user,yearID))
#---------------
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
#---------------
@require_POST
@csrf_exempt
def createSubject(request:HttpRequest):
    body:dict = json.loads(request.body)
    yearID = body.get("year_id",None)
    termID = body.get("term_id",None)
    name =body.get("name",None)
    return ResponseHelper(SubjectService().createSubject(request.user,yearID,termID,name))
#---------------
@require_GET
@csrf_exempt
def showLectures(request:HttpRequest)->JsonResponse:
    subjectID = request.GET.get("subject_id",None)
    return ResponseHelper(LectureService().showLectures(request.user,subjectID))
#---------------
@require_POST
@csrf_exempt
def createLectures(request:HttpRequest)->JsonResponse:
    body:dict = json.loads(request.body)
    name = body.get("name",None)
    subjectID = body.get("subject_id",None)
    return ResponseHelper(LectureService().createLectures(request.user,name,subjectID))
#---------------
@require_GET
@csrf_exempt
def showQuestions(request:HttpRequest)->JsonResponse:
    lecture = request.GET.get("lecture_id",None)
    return ResponseHelper(QuestionServices(request.user).showQuestions(lecture))
#---------------
@require_POST
@csrf_exempt
def createQuestion(request:HttpRequest)->JsonResponse:
    editor:QuestionFromFront = json.loads(request.body)
    return ResponseHelper(QuestionServices(request.user).createQuestion(editor))
#---------------
@api_view(['POST'])
@csrf_exempt
def createQuestions(request:HttpRequest)->JsonResponse:
    editor:list[QuestionFromFront] = json.loads(request.body)
    return ResponseHelper(QuestionServices(request.user).createQuestions(editor))
#---------------
@require_POST
@csrf_exempt
def createExam(request:HttpRequest)->JsonResponse:
    body:examRequest = cast(examRequest,json.loads(request.body))
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
    GES = GeneralExamServices(request.user)
    output = GES.createExamHybrid(body["title"],body["subject_id"],body["questions"],settings)
    if output["isSuccess"]:
        return ResponseHelper({"success":"exam created successfully"})
    return ResponseHelper(output)
#---------------
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
#---------------
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
    #---------------
    questions:list[QuestionToFront] = examCre["output"]#type:ignore
    sections:dict[str,list[QuestionToFront]] = {}
    for i,q in enumerate(questions):
        if not q["sectionName"] in sections:
            if not q["sectionName"]:
                q["sectionName"] = ""
            #---------------
            sections[q["sectionName"]] = [q]
            continue
        #---------------
        sections[q["sectionName"]].append(q)
    #---------------
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
#---------------
@require_POST
@csrf_exempt
def createClassRoom(request:HttpRequest):#tested
    """
    creating classroom needs the following fields in body:
        title
        HideFromSearch
        paymentAmount
        PaymentExpireInterval_MIN
        PaymentAccessMaxCount
    """
    body = cast(ClassRoomFromFrontend,json.loads(request.body))
    user = cast(IUserHelper,request.user)
    clService = classRoomService(user)
    return ResponseHelper(clService.createClassRoom(body))
#---------------
@require_GET
@csrf_exempt
def listclassRooms(request:HttpRequest):#tested
    user = cast(IUserHelper,request.user)
    clService = classRoomService(user)
    return ResponseHelper(clService.listClassRooms())
#---------------
@require_POST
@csrf_exempt
def assignExamToClassRoom(request:HttpRequest):
    user = cast(IUserHelper,request.user)
    body = json.loads(request.body)
    classRoomID:str|int = body.get("classRoom_ID",None)
    examID:str|int = body.get("exam_ID",None)
    if classRoomID and isinstance(classRoomID,str) and not classRoomID.isnumeric():
        classRoomID = int(classRoomID)
    #---------------
    if examID and isinstance(examID,str) and not examID.isnumeric():
        examID = int(examID)
    #---------------
    clService = classRoomService(user)
    currentclassRoom = clService.accessClassRoom(UserPrivileges.SOLVE_EXAM_ALLOWANCE)
    if not currentclassRoom["isSuccess"]:
        return currentclassRoom
    #---------------
    examServices = GeneralExamServices(user)
    exam = examServices.validateOwnerShip(cast(int,examID))
    if not exam["isSuccess"]:
        return currentclassRoom
    clService.addExam(currentclassRoom["output"],exam["output"]) #type:ignore
    return ResponseHelper(GOutput({"success":"exam assigend"})) 
#---------------
@require_POST
@csrf_exempt
def uploadAttachment(request:HttpRequest):
    user = cast(IUserHelper,request.user)
    classRoomID = request.POST.get('classRoom',None)
    paymentAmount = request.POST.get('paymentAmount',float(0))
    PaymentExpireInterval_MIN = request.POST.get('interval_min',0)
    PaymentAccessMaxCount = request.POST.get('maxCount',0)
    
    if isinstance(paymentAmount,str) and not paymentAmount.isnumeric():
        return ResponseHelper(GOutput(error={'paymentAmount':"must be a number"}))
    elif paymentAmount:
        paymentAmount = float(paymentAmount)
    #---------------
    if isinstance(PaymentExpireInterval_MIN,str) and not PaymentExpireInterval_MIN.isnumeric():
        return ResponseHelper(GOutput(error={'paymentAmount':"must be a number"}))
    elif PaymentExpireInterval_MIN:
        PaymentExpireInterval_MIN = int(PaymentExpireInterval_MIN)
    #---------------
    if isinstance(PaymentAccessMaxCount,str) and not PaymentAccessMaxCount.isnumeric():
        return ResponseHelper(GOutput(error={'paymentAmount':"must be a number"}))
    elif PaymentAccessMaxCount:
        PaymentAccessMaxCount = int(PaymentAccessMaxCount)
    #---------------
    
    if not classRoomID:
        return ResponseHelper(GOutput(error={'classRoom':"cannot be null"}))
    #---------------
    if classRoomID.isnumeric():
        classRoomID = int(classRoomID)
    #---------------
    clService = classRoomService(user)
    currentclassRoom = clService.accessClassRoom(classRoomID) #type:ignore
    if not currentclassRoom["isSuccess"]:
        return ResponseHelper(currentclassRoom)
    #---------------
    if not currentclassRoom["output"]:
        return ResponseHelper(GOutput(error={'fail':"something went wrong cannot access classroom"}))
    #---------------
    file = request.FILES["uploaded"]
    result = clService.addAttachment(currentclassRoom["output"],cast(InMemoryUploadedFile,file),paymentAmount,PaymentExpireInterval_MIN,PaymentAccessMaxCount) #type:ignore
    if not result["isSuccess"]:
        return ResponseHelper(result)
    return ResponseHelper(GOutput({"success":"attahcment uploaded"}))
#---------------
@require_GET
def listAttachment(request:HttpRequest):
    user = cast(IUserHelper,request.user)
    classRoomID = request.GET.get('classRoom')
    if not classRoomID:
        return ResponseHelper(GOutput(error={'classRoom':"cannot be null"}))
    #---------------
    if classRoomID.isnumeric():
        classRoomID = int(classRoomID)
    #---------------
    clService = classRoomService(user)
    currentclassRoom = clService.accessClassRoom(classRoomID) #type:ignore
    if not currentclassRoom["isSuccess"]:
        return ResponseHelper(currentclassRoom)
    #---------------
    if not currentclassRoom["output"]:
        return ResponseHelper(GOutput(error={'fail':"something went wrong cannot access classroom"}))
    attachments = clService.listAttachments(currentclassRoom["output"])
    return ResponseHelper(attachments)
#---------------
@require_POST
def createCommitte(request:HttpRequest):
    body:dict = json.loads(request.body)
    users = body.get("users",None)
    clRoomID = body.get('clsRoom',None)
    examID = body.get('examID',None)
    if not users:
        return ResponseHelper(GOutput(error={"users":"cannot be null"}))
    #---------------
    if not clRoomID:
        return ResponseHelper(GOutput(error={"clRoomID":"cannot be null"}))
    #---------------
    if not examID:
        return ResponseHelper(GOutput(error={"examID":"cannot be null"}))
    #---------------
    exam = Exam.objects.filter(ID=examID).first()
    if not exam:
        return ResponseHelper(GOutput(error={"exam":"is not found"}))
    #---------------
    clRoom = classRoom.objects.filter(ID=clRoomID).first()
    if not clRoom:
        return ResponseHelper(GOutput(error={"clRoom":"is not found"}),)
    #---------------
    try:
        admins = cast(list[IUserHelper],list(User.objects.filter(id__in=users).all()))
        user = request.user
        clService = classRoomService(user)
        clService.ManualcreateCommitee(clRoom,exam,admins)
    except Exception as e:
        return ResponseHelper(GOutput(error={"fail":"something went wrong"}))
#---------------
@require_POST
def joinCommitte(request:HttpRequest):
    body:dict = json.loads(request.body)
    committeID = body.get("committe_id",None)
    if not committeID:
        return ResponseHelper(GOutput(error={"committe":"cannot be null"}))
    #---------------
    committe = Committe.objects.filter(id=committeID).first()
    if not committe:
        return ResponseHelper(GOutput(error={"committe":"cannot be null"}))
    #---------------
    user = cast(IUserHelper,request.user)
    committeService = CommitteServices(user)
    return ResponseHelper(committeService.join(committe))
#---------------
@require_GET
@csrf_exempt
def showExamOutOfCommit(request:HttpRequest):
    user = cast(IUserHelper,request.user)
    examID = request.GET.get("exam_id",None)
    if not examID:
        return ResponseHelper(GOutput(error={"exam_id":"cannot be null"}))
    examService = GeneralExamServices(user)
    exam:Optional[Exam] = user.Exams.filter(ID=examID).first()
    if not exam:
        return ResponseHelper(GOutput(error={"exam":"is not found"}))
    frontEndData = examService.sendCredentials(exam)
    return ResponseHelper(frontEndData)
#------------------
@require_POST
def showExam(request:HttpRequest):
    body:dict = json.loads(request.body)
    committeID = body.get("committe_id",None)
    passkey = body.get("passkey",None)
    user = cast(IUserHelper,request.user)
    committeOuput = CommitteServices.getCommitte(committeID)
    if not committeOuput["isSuccess"]:
        return ResponseHelper(committeOuput)
    #---------------
    committe = cast(Committe,committeOuput["output"])
    committeService = CommitteServices(user)
    return ResponseHelper(committeService.getExamCredentials(committe,passkey))
#---------------
@require_POST
def startCommitte(request:HttpRequest):
    body:dict = json.loads(request.body)
    user = cast(IUserHelper,request.user)
    committeID = body.get("committe_id",None)
    committeOuput = CommitteServices.getCommitte(committeID)
    if not committeOuput["isSuccess"]:
        return ResponseHelper(committeOuput)
    #---------------
    committeService = CommitteServices(user)
    committeService.startCommitte(committeOuput["output"])#type:ignore
    return ResponseHelper(GOutput({"success":"commmitte started"}))
#---------------
@require_POST
def solveExam(request:HttpRequest):
    body:dict = json.loads(request.body)
    user = cast(IUserHelper,request.user)
    committeService = CommitteServices(user)
    questionID = body.get("qID",None)
    if not questionID:
        return ResponseHelper(GOutput(error={"qID":"cannot be null"}))
    #---------------
    passkey = body.get("passkey",None)
    if not passkey:
        return ResponseHelper(GOutput(error={"passKey":"cannot be null"}))
    #---------------
    committeID = body.get("committe_id",None)
    if not committeID:
        return ResponseHelper(GOutput(error={"committeID":"cannot be null"}))
    #---------------
    ans = body.get("ans",None)
    if not ans:
        return ResponseHelper(GOutput(error={"ans":"cannot be null"}))
    #---------------
    location:Location_Type = cast(Location_Type,body.get("location",None))
    if not location or not location["Xaxis"] or not location["Yaxis"]:
        return ResponseHelper(GOutput(error={"ans":"cannot be null"}))
    #---------------
    committeOuput = CommitteServices.getCommitte(committeID)
    committe = committeOuput["output"]
    if not committe:
        return ResponseHelper(GOutput(error={"committe":"not found"}))
    #---------------
    committeService.solveExam(questionID,passkey,committe,ans,location)
    return ResponseHelper(GOutput({"success":"commmitte started"}))
#---------------