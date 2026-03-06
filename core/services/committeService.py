from datetime import datetime
from typing import Optional

from core.models.Exams_models import Committe, CommitteEvents, Exam
from core.services.examService import OnlineExam
from core.services.types.examTypes import Location_Type
from core.services.types.questionType import GeneralOutput, QuestionToFront
from core.services.types.userType import IUserHelper
from core.services.utils.generalOutputHelper import GOutput
from django.db import transaction


"""
#---------------#---------------#-----------
# In committe class we have 3 vary important flags
#---------------#---------------#-----------
isOpened - This means that inspector allow users to connect
isinspectorIn - This means that inspector in or joined 
isExamStarted - This means that allow user to get exam credintials

"""


class CommitteServices:
    def __init__(self,requester:IUserHelper ,*args, **kwargs):
        self.Requester = requester
    #---------------
    @staticmethod
    def getCommitte(committeID)->GeneralOutput[Optional[Committe]]:
        if not committeID:
            return GOutput(error={"committe":"cannot be null"})
        #---------------
        if isinstance(committeID,str):
            committeID = int(committeID)
        #---------------
        committe = Committe.objects.filter(id=committeID).first()
        if not committe:
            return GOutput(error={"committe":"cannot be null"})
        #---------------
        return GOutput(committe)
    #---------------
    def _logger(self,eventName:str,committe:Committe):
        eventStr:str = f"[{datetime.now().isoformat()}] - ({self.Requester.username}):{eventName}"#type:ignore
        CommitteEvents.objects.create(
            eventStr=eventStr,
            committe=committe
        )
    #---------------
    @transaction.atomic
    def startCommitte(self,committe:Committe):
        """inspector joining event"""
        if committe.inspector != self.Requester:
            self._logger("trying to start committe without permission",committe)
            return
        #---------------
        self._logger("starting committe",committe)
        committe.isOpened = True
        committe.save()
    #---------------
    @transaction.atomic
    def join(self,committe:Committe)->GeneralOutput:
        """student joining event"""
        if self.Requester == committe.inspector:
            self._logger("inspector joined committe",committe)
            committe.isInspectorIn = True
            committe.save()
            return GOutput({"success":"inspector joined"})
        #---------------
        studentRow = committe.allowList.filter(users=self.Requester).first()
        if studentRow:
            self._logger("student joined",committe)
            studentRow.present = True
            studentRow.save()
            return GOutput({"success":"student joined"})
        #---------------
        self._logger("unauthorized user trying to join",committe)
        return GOutput(error={"unauthorized":"joining faild"})
    #---------------
    @transaction.atomic
    def startExam(self,committe:Committe)->GeneralOutput:
        """starting exam event"""
        if self.Requester == committe.inspector and not committe.isExamStarted:
            self._logger("inspector started exam",committe)
            committe.isExamStarted = True
            committe.save()
            return GOutput({"success":"exam started"})
        #---------------
        self._logger("unauthorized access trying to start exam",committe)
        return GOutput(error={"unauthorized":"cannot start exam"})
    #---------------
    def getExamCredentials(self,committe:Committe,passKey:str | None)->GeneralOutput[list[QuestionToFront] | None]:
        if self.Requester == committe.inspector:
            self._logger("inspector accessed exam",committe)
        #---------------
        else:
            self._logger("student accessed exam",committe)
        #---------------
        examService = OnlineExam(self.Requester)
        ExamCredentials = examService.sendCredentials(committe.Exam,passKey)
        return ExamCredentials
    #---------------
    def solveExam(self,questionID:str|int,passKey:str,committe:Committe,ans:str,location:Location_Type)->GeneralOutput:
        """solve exam event"""
        if self.Requester == committe.inspector:
            self._logger("inspector trying to solve exam",committe)
            return GOutput(error={"unauthorized":"inspector cannot solve exam"})
        #---------------
        exam:Exam = committe.Exam
        inAllowedstudent = committe.allowList.filter(self.Requester).first()
        if not inAllowedstudent:
            self._logger("tried to solve exam",committe)
            return GOutput(error={"unauthorized":"student cannot solve exam in this committe"})
        #---------------
        q = exam.Questions.filter(ID=questionID).first()
        if not q:
            return GOutput(error={"fail":"Cannot solve not exist question"})
        examServices = OnlineExam(self.Requester)
        examServices.autoSave(exam,passKey,q,self.Requester,ans,location)
        return GOutput({"success":"exam solved successfully"})
    #---------------
#---------------CLASS-ENDED#---------------