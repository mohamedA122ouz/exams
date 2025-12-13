from typing import cast
from core.models.Exams_models import Exam, Question, Settings
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
            Exam=exam
        )
    #------------------
    def createExam(self,title,subject_id,Question_ids:list[int],classRoom:int):
        # Title
        # Subject
        # Questions
        # Settings
        subject = self.Owner.Subjects.filter(ID = subject_id)
        exam = self.Owner.Exams.create(
            Title=title,
            Subject = subject
        )
        questions = Question.objects.filter(ID__in=Question_ids)
        self.defaultExamSettings(exam,30)#trying 30min
        exam.Questions.set(questions)
    #------------------
#------------------CLASS-ENDED#------------------