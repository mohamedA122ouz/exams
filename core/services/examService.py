from datetime import datetime
from typing import Optional, cast
from core.models.Exams_models import Exam, ExamQuestion, Question, Settings
from core.services.types.examTypes import ExamSettings
from core.services.types.questionType import ShareWithEnum
from core.services.types.userType import IUserHelper

class GeneralExamServices:
    INITIAL_SETTINGS:ExamSettings = {
        "AllowDownLoad":True,
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
            AllowDownLoad = settings["AllowDownLoad"],
            StartAt = settings["StartAt"],
            EndAt = settings["EndAt"],
            Exam=exam,
            PreventOtherTabs=settings["PreventOtherTabs"]
        )
        if settings["Locations"]:
            examCurrentSettings.Locations.create(Xaxis=settings["Locations"]["Xaxis"],Yaxis=settings["Locations"]["Yaxis"])
    #------------------
    def createExam(self,title:str,subject_id:int,Question_ids:list[int],settings:ExamSettings):
        if not title:
            return {"title":"cannot be null"}
        if not subject_id: 
            return {"subject_id":"cannot be null"}
        if not Question_ids:
            return {"Question_ids":"cannot be null"}
        subject = self.Owner.Subjects.filter(ID = subject_id).first()
        if not subject:
            return {"subject":"not found in your Subjects"}
        exam = self.Owner.Exams.create(
            Title=title,
            Subject = subject
        )
        questions = Question.objects.filter(ID__in=Question_ids)
        exam_questions = [
            ExamQuestion(Exam=exam, Question=q, Order=i+1)
            for i, q in enumerate(questions)
        ]
        ExamQuestion.objects.bulk_create(exam_questions)
        self.defaultExamSettings(exam,settings)#trying 30min
    #------------------
    def assignExamToClassRoom(self,exam:Exam,classroom_id:int):
        classRoom = self.Owner.OwnedClasses.filter(ID=classroom_id).first()
        if classRoom:
            classRoom.Exams.add(exam)
        #------------------
#------------------CLASS-ENDED#------------------