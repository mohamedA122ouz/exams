from datetime import datetime
from typing import Any, Optional, cast
from core.models.Exams_models import Exam, ExamQuestion, Question, Settings
from core.services.types.examTypes import ExamSettings
from core.services.types.questionType import QuestionFromFront, ShareWithEnum
from core.services.types.userType import IUserHelper
from core.services.utils.examParser import toFrontendForm, toFrontendFormHelper, toDBFromParser
from django.db.models import F

class GeneralExamServices:
    INITIAL_SETTINGS:ExamSettings = {
        "AllowDownload":True,
        "AutoCorrect":True,
        "Duration_min":60,
        "EndAt":None,
        "StartAt":None,
        "Locations":None,
        "PreventOtherTabs":True,
        "QuestionByQuestion":False,
        "ShareWith":ShareWithEnum.PRIVATE
    }
    def __init__(self,user) -> None:
        self.Owner:IUserHelper = cast(IUserHelper,user)
    def defaultExamSettings(self,exam,settings:ExamSettings):
        if settings["Duration_min"] == 0:
            settings = self.INITIAL_SETTINGS
            raise Exception("duration error cannot be 0")
        if not settings:
            settings = self.INITIAL_SETTINGS
        examCurrentSettings = Settings(
            Duration_min=settings,
            AutoCorrect=settings["AutoCorrect"],
            QuestionByQuestion=settings["QuestionByQuestion"],
            ShareWith=settings["ShareWith"].value,
            AllowDownLoad = settings["AllowDownload"],
            StartAt = settings["StartAt"],
            EndAt = settings["EndAt"],
            Exam=exam,
            PreventOtherTabs=settings["PreventOtherTabs"]
        )
        if settings["Locations"]:
            examCurrentSettings.Locations.create(Xaxis=settings["Locations"]["Xaxis"],Yaxis=settings["Locations"]["Yaxis"])
    #------------------
    def pickExam(self,title:str,subject_id:int,Question_ids:list[int],settings:ExamSettings):
        if not title:
            return {"title":"cannot be null"}
        if not subject_id: 
            return {"subject_id":"cannot be null"}
        if not Question_ids:
            return {"Question_ids":"cannot be null"}
        subject = self.Owner.Subjects.filter(ID = subject_id).first()
        
        if not subject:
            return {"subject":"not exist"}
        if not "Duration_min" in settings:
            return {"settings":"settings.Duration_min cannot be null"}
        if not "AutoCorrect" in settings or not isinstance(settings["AutoCorrect"],bool):
            return {"settings":"settings.AutoCorrect cannot be null and it must be boolean"}
        if not "QuestionByQuestion" in settings or not isinstance(settings["QuestionByQuestion"],bool):
            return {"settings":"settins.QuestionsByQuestion cannot be null and must be boolean"}
        if not "AllowDownload" in settings or not isinstance(settings["AllowDownload"],bool):
            return {"settings":"settings.AllowDownload cannot be null and must be bool"}
        if not "StartAt" in settings or not isinstance(settings["StartAt"],datetime):
            return {"settings":"settings.StartAt cannot be null"}
        if not "EndAt" in settings:
            return {"settings":"settings.EndAt cannot be null"}
        if not "PreventOtherTabs":
            return {"settings":"settings.PreventOtherTabs cannot be null"}
        questions = Question.objects.filter(ID__in=Question_ids)
        if len(questions) == 0:
            return {"questions":"not exist"}
        exam = self.Owner.Exams.create(
            Title=title,
            Subject = subject
        )
        exam_questions = [
            ExamQuestion(Exam=exam, Question=q, Order=i+1)
            for i, q in enumerate(questions)
        ]
        questions.update(InExamCounter=F("InExamCounter")+1)
        createdObjects = ExamQuestion.objects.bulk_create(exam_questions)
        self.defaultExamSettings(exam,settings)
        if len(createdObjects) == len(exam_questions):
            
            return {"success":"object created"}
        return {"faild":"something not created or something error"}
    #------------------
    def assignExamToClassRoom(self,exam:Exam,classroom_id:int):
        classRoom = self.Owner.OwnedClasses.filter(ID=classroom_id).first()
        if classRoom:
            classRoom.Exams.add(exam)
            return {"success":"exam assigned"}
        #------------------
        return {"classroom_id":"user don't have classroom with the given ID"}
    #------------------
    def createExam(self,input:list[QuestionFromFront],title:str,subject_id:int,settings:ExamSettings):
        """Create full exam from scratch"""
        if not title:
            return {"title":"cannot be null"}
        if not subject_id and isinstance(subject_id,int):
            return {"subject_id":"cannot be null and must be int"}
        questions:list[Question] = []
        error:dict[str,Any] = {}
        for i in input:
            output = toDBFromParser(i)
            if output["isSuccess"]:
                q = output["output"]
                questions.append(Question(
                    Text_Url = q["question"],
                    Type = q["type"],
                    Ans = q["ans"],
                    Lecture_id = q["lecture_id"],
                    Ease = q["ease"],
                    InExamCounter = 1
                ))
            #------------------
            elif not output["isSuccess"] and output["error"]:
                error = output["error"]
                break
            #------------------
            else:
                error = {"input":"unexpected error"}
                break
            #------------------
        #------------------
        if len(questions) != len(input):
            return error
        #------------------
        self.Owner.Questions.bulk_create(questions)
        exam = self.Owner.Exams.create(
            Title=title,
            Subject_id = subject_id
        )
        exam_questions = [
            ExamQuestion(Exam=exam, Question=q, Order=i+1)
            for i, q in enumerate(questions)
        ]
        self.defaultExamSettings(exam,settings)
        if len(questions) == len(exam_questions):
            return {"success":"objects created"}
        return {"faild":"something not created or something error"}
#------------------CLASS-ENDED#------------------