from typing import cast
from core.models.Exams_models import Exam, ExamQuestion, Question, Settings
from core.services.types.questionType import ShareWithEnum
from core.services.types.userType import IUserHelper


class GeneralExamServices:
    def __init__(self,user) -> None:
        self.Owner:IUserHelper = cast(IUserHelper,user)
    def defaultExamSettings(self,exam,duration_min:int):
        return Settings.objects.create(
            Duration_min=duration_min,
            AutoCorrect=True,
            QuestionByQuestion=False,
            ShareWith=ShareWithEnum.PRIVATE.value,
            AllowDownLoad = True,
            StartAt = None,
            EndAt = None,
            Exam=exam,
            PreventOtherTabs=True
        )
    #------------------
    def createExam(self,title:str,duration:int,subject_id:int,Question_ids:list[int]):
        if not title:
            return {"title":"cannot be null"}
        if not subject_id: 
            return {"subject_id":"cannot be null"}
        if not Question_ids:
            return {"Question_ids":"cannot be null"}
        if not duration:
            return {"duration":"cannot be null"}
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
        self.defaultExamSettings(exam,30)#trying 30min
    #------------------
    def assignExamToClassRoom(self,exam:Exam,classroom_id:int):
        classRoom = self.Owner.OwnedClasses.filter(ID=classroom_id).first()
        if classRoom:
            classRoom.Exams.add(exam)
        #------------------
#------------------CLASS-ENDED#------------------