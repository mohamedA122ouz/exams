from datetime import datetime
from typing import Optional

from core.models.Exams_models import Committe, CommitteEvents, Exam, Question, classRoom
from core.services.ServiceProviders import BaseServiceProvider
from core.services.classRoomService import checkForPrivilege, classRoomService
from core.services.examService import OnlineExam
from core.services.types.examTypes import Location_Type
from core.services.types.questionType import GeneralOutput, QuestionToFront
from core.services.types.userType import IUserHelper
from core.services.utils.generalOutputHelper import GOutput
from django.db import transaction

from core.services.utils.privileges import UserPrivileges


"""
#---------------#---------------#-----------
# In committe class we have 3 vary important flags
#---------------#---------------#-----------
isOpened - This means that inspector allow users to connect
isinspectorIn - This means that inspector in or joined 
isExamStarted - This means that allow user to get exam credintials

"""


class CommitteServices(BaseServiceProvider):
    def __init__(self,requester:IUserHelper,classRoom:classRoom ,*args, **kwargs):
        super().__init__(requester,classRoom,*args, **kwargs)
        
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
        self._logger(f"inspector {self.Requester.username} starting committe",committe)#type:ignore
        committe.isOpened = True
        committe.save()
    #---------------
    @transaction.atomic
    def join(self,committe:Committe)->GeneralOutput:
        """student joining event"""
        if self.Requester == committe.inspector:
            self._logger(f"inspector {self.Requester.username} joined committe",committe)#type:ignore
            committe.isInspectorIn = True
            committe.save()
            return GOutput({"success":"inspector joined"})
        #---------------
        studentRow = committe.allowList.filter(users=self.Requester).first()
        if studentRow:
            self._logger(f"student {self.Requester.username} joined",committe) #type:ignore
            studentRow.present = True
            studentRow.save()
            return GOutput({"success":"student joined"})
        #---------------
        self._logger(f"unauthorized user {self.Requester.username} trying to join",committe) #type:ignore
        return GOutput(error={"unauthorized":"joining failed"})
    #---------------
    @transaction.atomic
    def startExam(self,committe:Committe)->GeneralOutput:
        """starting exam event"""
        if self.Requester == committe.inspector and not committe.isExamStarted:
            self._logger(f"inspector {self.Requester.username} started exam",committe) #type:ignore
            committe.isExamStarted = True
            committe.save()
            return GOutput({"success":"exam started"})
        #---------------
        self._logger(f"unauthorized user {self.Requester.username} trying to start exam",committe) #type:ignore
        return GOutput(error={"unauthorized":"cannot start exam"})
    #---------------
    def getExamCredentials(self,committe:Committe,passKey:str | None)->GeneralOutput[list[QuestionToFront] | None]:
        if self.Requester == committe.inspector:
            self._logger(f"inspector {self.Requester.username} accessed exam",committe) #type:ignore
        #---------------
        else:
            self._logger(f"student {self.Requester.username} accessed exam",committe) #type:ignore
        #---------------
        examService = OnlineExam(self.Requester,self.ProvidedObject)
        ExamCredentials = examService.sendCredentials(committe.Exam,passKey)
        return ExamCredentials
    #---------------
    def getExamChunks(self,committe:Committe,passKey:str | None,qIndex:list[int])->GeneralOutput[Optional[QuestionToFront]]:
        if self.Requester == committe.inspector:
            self._logger(f"inspector {self.Requester.username} accessed exam questions {str(qIndex)}",committe) #type:ignore
        #---------------
        else:
            self._logger(f"student {self.Requester.username} accessed exam questions {str(qIndex)}",committe) #type:ignore
        #---------------
        ExamChunk = committe.Exam.objects.filter(Questions__InExamCounter__in=qIndex).values('Questions__ID','Questions__Title','Questions__Type','Questions__InExamCounter')
        return ExamChunk
    #------------------
    # this function is so slow cause the function is checking every time it auto saves whether this 
    # student have the ability to solve the question or not which is not necessary cause the system already
    # check at the first run and it is websocket so it is not stateless
    def solveExam(self,questionID:str|int,passKey:str,committe:Committe,ans:str,location:Location_Type)->GeneralOutput:
        """solve exam event"""
        if self.Requester == committe.inspector:
            self._logger(f"inspector {self.Requester.username} trying to solve exam",committe) #type:ignore
            return GOutput(error={"unauthorized":"inspector cannot solve exam"})
        #---------------
        exam:Exam = committe.Exam
        inAllowedstudent = committe.allowList.filter(self.Requester).first()
        if not inAllowedstudent:
            self._logger(f"student {self.Requester.username} tried to solve exam",committe) #type:ignore
            return GOutput(error={"unauthorized":"student cannot solve exam in this committe"})
        #---------------
        q = exam.Questions.filter(ID=questionID).first()
        if not q:
            return GOutput(error={"fail":"Cannot solve not exist question"})
        examServices = OnlineExam(self.Requester,self.ProvidedObject)
        examServices.autoSave(exam,passKey,q,self.Requester,ans,location)
        return GOutput({"success":"exam solved successfully"})
    #---------------
    def fastSolveExam(self,questionID:str|int,passKey:str,committe:Committe,ans:str,location:Location_Type)->GeneralOutput:
        """this function is for testing purposes only and it is not checking any permissions"""
        exam:Exam = committe.Exam
        q = exam.Questions.filter(ID=questionID).first()
        if not q:
            return GOutput(error={"fail":"Cannot solve not exist question"})
        examServices = OnlineExam(self.Requester,self.ProvidedObject)
        examServices.autoSave(exam,passKey,q,self.Requester,ans,location)
        return GOutput({"success":"exam solved successfully"})
    #------------------
    @transaction.atomic
    @checkForPrivilege(privilege=UserPrivileges.ADD_STUDENTS)
    def _addStudent(self,committe:Committe,student:IUserHelper)->GeneralOutput:
        """
        this add student without check if user already exist in a sibling committee 'NOT-SAFE'
        """
        self._logger(f"adding student {student.username} to committe",committe) #type:ignore
        if not self.ProvidedObject:
            return GOutput(error={'student':"doesn't have privileges in the classRoom"})
        #---------------
        try:
            committe.allowList.create(users=student)
            return GOutput({'success':"user created successfully"})
        except Exception as e:
            return GOutput(error={"fail":"cannot add this user something went wrong"})
        #---------------
    #---------------
    @transaction.atomic
    @checkForPrivilege(privilege=UserPrivileges.ADD_STUDENTS)
    def addOrChangeStudentPlace(self,committe:Committe,student:IUserHelper,forceChange:bool):
        clsRoom:classRoom = committe.clRoom
        if not clsRoom:
            self._logger("committe doesn't have classRoom",committe)
            return GOutput(error={"committee":"committee doesn't have classRoom"})
        allCommittees = clsRoom.Committes
        if not allCommittees:
            self._logger("no committees found",committe)
            return GOutput(error={"committee":"no committees found"})
        #---------------
        for committee in allCommittees.all():
            if committee.allowList.contains(student): #type:ignore
                if not forceChange:
                    return GOutput(error={"student":"student already exist"})
                #---------------
                else:
                    allowList = committee.allowList.filter(users=student).first()
                    if not allowList:
                        return GOutput(error={"student":"student not found in committee"})
                    #---------------
                    allowList.delete()
                    return self._addStudent(committee,student)
                #---------------
            #---------------
        #---------------
    #---------------
#---------------CLASS-ENDED#---------------