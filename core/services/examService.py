from datetime import datetime
from typing import Any, Optional, cast
from core.models.Exams_models import Exam, ExamBlackList, ExamQuestion, Question
from core.services.types.examTypes import ExamSettings
from core.services.types.questionType import ExamAutoGenerator, QuestionFromFront, QuestionSelector, ShareWithEnum, GeneralOutput
from core.services.types.userType import IUserHelper
from core.services.utils.examParser import autoGeneratorParser, toDBFromParser
from django.db.models import F
from django.contrib.auth.models import User

from core.services.utils.generalOutputHelper import GOutput

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
    #------------------
    def _resetDefaultSettings(self,exam:Exam)->dict[str,str]:
        exam.AllowDownLoad = self.INITIAL_SETTINGS["AllowDownload"]
        exam.AutoCorrect = self.INITIAL_SETTINGS["AutoCorrect"]
        exam.Duration_min = self.INITIAL_SETTINGS["Duration_min"]
        exam.EndAt = self.INITIAL_SETTINGS["EndAt"]
        exam.ShareWith = self.INITIAL_SETTINGS["ShareWith"]
        exam.StartAt = self.INITIAL_SETTINGS["StartAt"]
        exam.PreventOtherTabs = self.INITIAL_SETTINGS["PreventOtherTabs"]
        exam.QuestionByQuestion = self.INITIAL_SETTINGS["QuestionByQuestion"]
        exam.Locations.all().delete()
        return {"success":"settings is resetted"}
    #------------------
    def updateSettings(self,exam:Exam,settings:ExamSettings):
        if not "AllowDownload" in settings:
            return {"AllowDownload":"cannot be null"}
        if not "AutoCorrect" in settings:
            return {"AutoCorrect":"cannot be null"}
        if not "Duration_min" in settings:
            return {"Duration_min":"cannot be null"}
        if not "EndAt" in settings:
            return {"EndAt":"cannot be null"}
        if not "ShareWith" in settings:
            return {"ShareWith":"cannot be null"}
        if not "PreventOtherTabs":
            return {"PreventOtherTabs":"cannot be null"}
        if not "QuestionByQuestion" in settings:
            return {"QuestionByQuestion":"cannot be null"}
        exam.AllowDownLoad = settings["AllowDownload"]
        exam.AutoCorrect = settings["AutoCorrect"]
        exam.Duration_min = settings["Duration_min"]
        exam.EndAt = settings["EndAt"]
        exam.ShareWith = settings["ShareWith"]
        exam.StartAt = settings["StartAt"]
        exam.PreventOtherTabs = settings["PreventOtherTabs"]
        exam.QuestionByQuestion = settings["QuestionByQuestion"]
        exam.save()
        return {"success":"settings is resetted successfully"}
    #------------------
    def _setExamSettings(self,exam:Exam,settings:ExamSettings):
        if settings["Duration_min"] == 0:
            settings = self.INITIAL_SETTINGS
            raise Exception("duration error cannot be 0")
        if not settings:
            settings = self.INITIAL_SETTINGS
        exam.AllowDownLoad = settings["AllowDownload"]
        exam.AutoCorrect = settings["AutoCorrect"]
        exam.Duration_min = settings["Duration_min"]
        exam.EndAt = settings["EndAt"]
        exam.ShareWith = settings["ShareWith"]
        exam.StartAt = settings["StartAt"]
        exam.PreventOtherTabs = settings["PreventOtherTabs"]
        exam.QuestionByQuestion = settings["QuestionByQuestion"]
        if settings["Locations"]:
            exam.Locations.create(Xaxis=settings["Locations"]["Xaxis"],Yaxis=settings["Locations"]["Yaxis"])
    #------------------
    def _manualPickQuestion(self,title:str,subject_id:int,Question_ids:list[int],settings:ExamSettings,exam:Optional[Exam] = None)->GeneralOutput[Optional[Exam]]:
        if not title:
            return GOutput(error={"title":"cannot be null"})
        if not subject_id: 
            return GOutput(error={"subject_id":"cannot be null"})
        if not Question_ids:
            return GOutput(error={"Question_ids":"cannot be null"})
        subject = self.Owner.Subjects.filter(ID = subject_id).first()
        if not subject:
            return GOutput(error={"subject":"not exist"})
        if not "Duration_min" in settings:
            return GOutput(error={"settings":"settings.Duration_min cannot be null"})
        if not "AutoCorrect" in settings or not isinstance(settings["AutoCorrect"],bool):
            return GOutput(error={"settings":"settings.AutoCorrect cannot be null and it must be boolean"})
        if not "QuestionByQuestion" in settings or not isinstance(settings["QuestionByQuestion"],bool):
            return GOutput(error={"settings":"settins.QuestionByQuestion cannot be null and must be boolean"})
        if not "AllowDownload" in settings or not isinstance(settings["AllowDownload"],bool):
            return GOutput(error={"settings":"settings.AllowDownload cannot be null and must be bool"})
        if not "PreventOtherTabs" in settings:
            return GOutput(error={"settings":"settings.PreventOtherTabs cannot be null"})
        questions = Question.objects.filter(ID__in=Question_ids)
        if len(questions) == 0:
            return GOutput(error={"questions":"not exist"})
        isAlreadyCreated = False
        if not exam:
            exam = self.Owner.Exams.create(
                Title=title,
                Subject = subject
            )
            isAlreadyCreated = True
        #------------------
        exam_questions = [
            ExamQuestion(Exam=exam, Question=q, Order=i+1)
            for i, q in enumerate(questions)
        ]
        questions.update(InExamCounter=F("InExamCounter")+1)
        createdObjects = ExamQuestion.objects.bulk_create(exam_questions)
        if not isAlreadyCreated:
            self._setExamSettings(exam,settings)
        #------------------
        if len(createdObjects) == len(exam_questions):
            return GOutput(exam)
        return GOutput(error={"faild":"something not created or something error"})
    #------------------
    def _assignExamToClassRoom(self,exam:Exam,classroom_id:int):
        classRoom = self.Owner.OwnedClasses.filter(ID=classroom_id).first()
        if classRoom:
            classRoom.Exams.add(exam)
            return {"success":"exam assigned"}
        #------------------
        return {"classroom_id":"user don't have classroom with the given ID"}
    #------------------
    def _createExam(self,input:list[QuestionFromFront],title:str,subject_id:int,settings:ExamSettings,exam:Optional[Exam]=None)->GeneralOutput[Optional[Exam]]:
        """Create full exam from scratch"""
        if not title:
            return GOutput(error={"title":"cannot be null"})
        if not subject_id and isinstance(subject_id,int):
            return GOutput(error={"subject_id":"cannot be null and must be int"})
        questions:list[Question] = []
        error:dict[str,Any] = {}
        for i in input:
            output = toDBFromParser(i)
            if output["isSuccess"]:
                q = output["output"]
                if not q:
                    return GOutput(error={"dbParser":"parser have error please contact admin"})
                #------------------
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
            return GOutput(error=error)
        #------------------
        self.Owner.Questions.bulk_create(questions)
        isAlreadyCreated = False
        if not exam:
            exam = self.Owner.Exams.create(
                Title=title,
                Subject_id = subject_id
            )
            isAlreadyCreated = True
        #------------------
        exam_questions = [
            ExamQuestion(Exam=exam, Question=q, Order=i+1)
            for i, q in enumerate(questions)
        ]
        if not isAlreadyCreated:
            self._setExamSettings(exam,settings)
        #------------------
        if len(questions) == len(exam_questions):
            return GOutput(exam)
        return GOutput(error={"faild":"something not created or something error"})
    #------------------
    def _createExamHybrid(self,title:str,subject_id:int,input:list[QuestionFromFront | ExamAutoGenerator|int],examSettings:ExamSettings)->GeneralOutput[Optional[Exam]]:
        manualPick:list[int] = [] # already exist question only choosing them manually
        autoPick:list[ExamAutoGenerator] = [] # already exist question only choosing them automatically
        manualQuestions:list[QuestionFromFront] = []
        
        for q in input:
            if isinstance(q,int):
                manualPick.append(q)
            elif "questions" in q and "generatorSettings" in q:
                autoPick.append(q)
            #------------------
            else:
                manualQuestions.append(q)
            #------------------
        #------------------
        questions = []
        for q in autoPick:
            questions += autoGeneratorParser(q,self.Owner)
        
        examSelectorOutput = self._manualPickQuestion(title,subject_id,manualPick,examSettings)
        if not examSelectorOutput["isSuccess"]:
            return examSelectorOutput # an error for sure
        exam:Exam = examSelectorOutput["output"] #type:ignore
        output = self._createExam(manualQuestions,title,subject_id,examSettings,exam)
        if not output["isSuccess"]:
            return output
        return GOutput(exam)
    #------------------
    def print(self)->GeneralOutput[Any]:
        ...
    #------------------
    def mark(self)->None:
        ...
    #------------------
    def blackListStudent(self,student:IUserHelper,exam:Exam,reason:str)->GeneralOutput:
        """kick this student from the current exam session and add him/her to blacklist so they cannot enter it back"""
        if student == self.Owner:
            return GOutput(error={"blacklist":"cannot ban the owner"})
        ExamBlackList.objects.create(
            student=student,
            exams=exam,
            Reason=reason
        )
        return GOutput({"success":"student is banned"})
    #------------------
    def createExamFromPDF(self)->dict[str,str]:
        ...
    #------------------
    def createExamFromWord(self)->dict[str,str]:
        ...
    #------------------
    def checkPermission(self)->dict[str,str]:
        ...
    #------------------
#------------------CLASS-ENDED#------------------

class OnlineExam(GeneralExamServices):
    def blackListStudent(self, student: IUserHelper, exam: Exam, reason: str) -> GeneralOutput:
        output = super().blackListStudent(student, exam, reason)
        if not output["isSuccess"]:
            return output
        exam.ExamBlackListTable
    #------------------
    def _checkPassKey(self,passKey:str)->bool:
        ...
    #------------------
    def _checkGPS(self)->bool:
        ...
    #------------------
    def sendCredentials(self)->dict[str,str]:
        # isCheck = self._checkPassKey()
        # if not isCheck:
            # return {"unauthorized":"cannot access thes exam"}
        ...
    #------------------
    def autoSave(self)->None:
        ...
    #------------------
    def submitWithReason(self,reason:str)->dict[str,str]:
        ...
    #------------------
    def activeUsers(self)->IUserHelper:
        ...
    #------------------
#------------------CLASS_ENDED#------------------
class OfflineExam(GeneralExamServices):
    def uploadExamPaper(self,bytes):
        ...
    #------------------
    def showExamPaper(self):
        ...
    #------------------
    def removeOldPapers(self):
        ...
    #------------------
#------------------CLASS_ENDED#------------------