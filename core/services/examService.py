from datetime import datetime, timedelta
from typing import Any, Optional, Union, cast
from core.models.Exams_models import Exam, Exam_BlackList, Exam_Questions, Location, Question, Soln, classRoom, classRoom_Exam, solutionsSheet
from core.services.classRoomService import classRoomService
from core.services.types.submitReason import SubmitReason
from core.services.types.examTypes import ExamSettings, Location_Type
from core.services.types.questionType import ExamAutoGenerator, QuestionFromFront, QuestionSelector, QuestionToFront, QuestionType, ScoringMode, ShareWithEnum, GeneralOutput
from core.services.types.userType import IUserHelper
from core.services.utils.examParser import autoGeneratorParser, toDBFormParser, toFrontendForm, toFrontendFormHelper
from django.db.models import F,QuerySet
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from core.services.utils.generalOutputHelper import GOutput
from core.services.utils.priviliages import UserPrivileges

class GeneralExamServices:
    INITIAL_SETTINGS:ExamSettings = {
        "PassKey":None,
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
        self.Requester:IUserHelper = cast(IUserHelper,user)
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
        #------------------
        exam.PassKey = settings["PassKey"]
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
        exam.save()
    #------------------
    def _manualPickQuestion(self,title:str,subject_id:int,Question_ids:list[int],settings:ExamSettings,exam:Optional[Exam] = None)->GeneralOutput[Optional[Exam]]:
        if not title:
            return GOutput(error={"title":"cannot be null"})
        if not subject_id: 
            return GOutput(error={"subject_id":"cannot be null"})
        if not Question_ids:
            return GOutput(error={"Question_ids":"cannot be null"})
        subject = self.Requester.Subjects.filter(ID = subject_id).first()
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
            exam = self.Requester.Exams.create(
                Title=title,
                Subject = subject
            )
            isAlreadyCreated = True
        #------------------
        exam_questions = [
            Exam_Questions(Exam=exam, Question=q, Order=i+1)
            for i, q in enumerate(questions)
        ]
        questions.update(InExamCounter=F("InExamCounter")+1)
        createdObjects = Exam_Questions.objects.bulk_create(exam_questions)
        if not isAlreadyCreated:
            self._setExamSettings(exam,settings)
        #------------------
        if len(createdObjects) == len(exam_questions):
            return GOutput(exam)
        return GOutput(error={"faild":"something not created or something error"})
    #------------------
    def _assignExamToClassRoom(self,exam:Exam,classroom_id:int):
        classRoom = self.Requester.OwnedClasses.filter(ID=classroom_id).first()
        if classRoom and exam.Owner == self.Requester:
            classRoom.Exams.add(exam)
            return {"success":"exam assigned"}
        #------------------
        return {"classroom_id":"user don't have classroom with the given ID"}
    #------------------
    def _createExam(self,input:list[QuestionFromFront],title:str,subject_id:int,settings:ExamSettings,exam:Optional[Exam]=None)->GeneralOutput[Optional[Exam]]:
        """Create full exam from scratch"""
        createdAt = datetime.now()
        if not title:
            return GOutput(error={"title":"cannot be null"})
        if not subject_id and isinstance(subject_id,int):
            return GOutput(error={"subject_id":"cannot be null and must be int"})
        questions:list[Question] = []
        sectionsArr:list[Optional[str]] = []
        error:dict[str,Any] = {}
        fullMark:float = 0
        for i in input:
            output = toDBFormParser(i)
            if output["isSuccess"]:
                q = output["output"]
                if not q:
                    return GOutput(error={"dbParser":"parser have error please contact admin"})
                #------------------
                if "sectionName" in i:
                    sectionsArr.append(i["sectionName"])
                else:
                    sectionsArr.append(None)
                if "degree" in i and i["degree"]:
                    fullMark += i["degree"]
                else:
                    return GOutput(error={"degree":"cannot have a question in an exam with no degrees"})
                #------------------
                questions.append(Question(
                    Text_Url = q["question"],
                    Type = q["type"],
                    Ans = q["ans"],
                    Lecture_id = q["lecture_id"],
                    Ease = q["ease"],
                    InExamCounter = 1,
                    createdAt=createdAt,
                    OwnedBy=self.Requester
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
        createdQs = self.Requester.Questions.bulk_create(questions)
        isAlreadyCreated = False
        if not exam:
            exam = self.Requester.Exams.create(
                TotalMark=fullMark,
                Title=title,
                Subject_id = subject_id
            )
            isAlreadyCreated = True
        #------------------
        exam_questions = [
            Exam_Questions(Exam=exam, Question=q, Order=i+1,sectionName=sectionsArr[i],degree=input[i]["degree"])
            for i, q in enumerate(createdQs)
        ]
        Exam_Questions.objects.bulk_create(exam_questions)
        if isAlreadyCreated:
            self._setExamSettings(exam,settings)
        #------------------
        if len(questions) == len(exam_questions):
            return GOutput(exam)
        return GOutput(error={"faild":"something not created or something error"})
    #------------------
    def createExamHybrid(self,title:str,subject_id:int,input: list[QuestionFromFront]|list[ExamAutoGenerator]|list[int],examSettings:ExamSettings)->GeneralOutput:
        manualPick:list[int] = [] # already exist question only choosing them manually
        autoPick:list[ExamAutoGenerator] = [] # already exist question only choosing them automatically
        manualQuestions:list[QuestionFromFront] = []
        mainExam:Optional[Exam] = None
        
        # clustering exam questions from frontend
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
        # create picking only the questions wihthout creating the exam
        questions:list[Question] = []
        for q in autoPick:
            questionOutput = autoGeneratorParser(q,self.Requester) # create the question but not the exam it self
            if questionOutput["isSuccess"] and questionOutput["output"]:
                questions += questionOutput["output"]
        #------------------
        if len(questions) > 0:
            if not mainExam:
                mainExam = self.Requester.Exams.create(
                    Title=title,
                    Subject_id = subject_id
                )
            #------------------
            exam_questions = [
                Exam_Questions(Exam=mainExam, Question=q, Order=i+1)
                for i, q in enumerate(questions)
            ]
            Exam_Questions.objects.bulk_create(exam_questions)
        #------------------
        examSelectorOutput = self._manualPickQuestion(title,subject_id,manualPick,examSettings,mainExam)
        if examSelectorOutput["isSuccess"] and not mainExam:
            mainExam = examSelectorOutput["output"] # an error for sure
        # #------------------
        output = self._createExam(manualQuestions,title,subject_id,examSettings,mainExam)
        if output["isSuccess"] and not mainExam:
            mainExam = output["output"]
        if not mainExam:
            return GOutput(error={"faild":"exam creation faild"})
        return GOutput({"success":"created successfully"})
    #------------------
    # passKey not needed here but the I have to write it cause no method overload her in python
    def  sendCredentials(self,exam:Exam,passKey:Optional[str]=None)->GeneralOutput[Optional[list[QuestionToFront]]]:
        if exam.PassKey and exam.PassKey != passKey and self.Requester != exam.Owner:
            return GOutput(error={"unauthorized":"cannot get exam with wrong passkey"})
        if self.Requester != exam.Owner and exam.ShareWith == ShareWithEnum.PRIVATE.value:
            return GOutput(error={"unauthorized":"cannot get exam for None Owner"})
        elif self.Requester != exam.Owner and exam.ShareWith == ShareWithEnum.CLASSROOM_DEFAULT.value:
            allClassRoomsStudyat = [privilege.ClassRooms for privilege in self.Requester.Privileges.all()] # there could be a better solution but it is what it is for now
            isInClassRoom = classRoom_Exam.objects.filter(exams=exam,classRoom__in = allClassRoomsStudyat).first()
            classRoomAuthenticator = classRoomService(self.Requester)
            if not isInClassRoom:
                return GOutput(error={"unauthorized":"cannot get exam for None Owner"})
            #------------------
            if classRoomAuthenticator._RequesterValidation(isInClassRoom.classRoom,UserPrivileges.SOLVE_EXAM_ALLOWANCE) and not (exam.StartAt or exam.EndAt): # if the user can solve exam and at the same time it is not specified schedular then is not accessable by those who can solve the exam
                return GOutput(error={"unauthorized":"this exam is private "})
            #------------------
            if classRoomAuthenticator._RequesterValidation(isInClassRoom.classRoom,UserPrivileges.SOLVE_EXAM_ALLOWANCE) and exam.StartAt < datetime.now() and exam.EndAt > datetime.now() :
                return GOutput(error={"unauthorized":"cannot get exam for None Owner"})
            #------------------
        #------------------
        questions:QuerySet[Exam_Questions,Exam_Questions] = Exam_Questions.objects.filter(Exam=exam).all()
        QtoFront:list[QuestionToFront] = cast(list[QuestionToFront],[])
        for q in questions:
            qfrontEnd = toFrontendFormHelper(q.Question)
            if qfrontEnd["isSuccess"] and qfrontEnd["output"] and len(qfrontEnd["output"]) == 1:
                del qfrontEnd["output"][0]["answers"] #type:ignore
                qfrontEnd["output"][0]["sectionName"] = q.sectionName
                qfrontEnd["output"][0]["ID"] = q.Question.ID
                QtoFront.append(qfrontEnd["output"][0]) #type:ignore
            #------------------
            else:
                return GOutput(error={"faild":"cannot access question"})
            #------------------
        #------------------
        return GOutput(QtoFront)
    #------------------
    def print(self)->GeneralOutput[Any]:
        exam = Exam.objects.first()
        if not exam:
            return GOutput(error={"faild":"no exam found"})
        examCre = self.sendCredentials(exam,"killer")
        if not examCre["isSuccess"] and not examCre["output"]:
            return examCre
        i = render_to_string("printingTemplates/examEN.html",{
            "title":exam.Title,
            "duration":exam.Duration_min,
            "subject":exam.Subject.Name,
            "mark":exam.TotalMark,
            "questions":examCre["output"],
            "year":exam.Subject.Year.Name,
            "startAt":exam.StartAt if exam.StartAt else datetime.now()
        })
        return GOutput(i)
    #------------------
    def autoMarking(self,classRoom,studentSheet:solutionsSheet):
        classRoomAuthenticator = classRoomService(self.Requester)
        output:GeneralOutput = classRoomAuthenticator._RequesterValidation(classRoom,UserPrivileges.CORRECTING_STUDENTS_SOLN)
        if not output["isSuccess"]:
            return output
        studentSheet.LastUpdate = datetime.now()
        SOLNS = studentSheet.Solns.all()
        WAITIN_AI_SOLN:list[Soln] = []
        for soln in SOLNS:
            soln.correctedBy = None
            ExamQuestion = Exam_Questions.objects.filter(Exam=solutionsSheet.Exam ,Question=soln.Question).first()
            if not ExamQuestion:
                return GOutput(error={"exam":"exam doesn't include this question"})
            #------------------
            FULL_MARK = ExamQuestion.degree
            if soln.Question.Type == QuestionType.COMPLEX or soln.Question.Type == QuestionType.WRITTEN_QUETION:
                WAITIN_AI_SOLN.append(soln)
            #------------------
            MODLE_ANS:list[str] = sorted(cast(str,soln.Question.Ans).split(','))
            STUDENT_ANS:list[str] = sorted(cast(str,soln.Content).split(','))
            correctAnsCount = 0
            for i,ans in enumerate(MODLE_ANS):
                if ans == STUDENT_ANS[i]:
                    correctAnsCount += 1
                #------------------
            #------------------
            PERCENTAGE =  correctAnsCount/len(MODLE_ANS)
            if soln.Question.scoringMode == ScoringMode.MULTI_ANS_ONE_ENOUGH:
                soln.Degree = FULL_MARK
                studentSheet.TotalMark += FULL_MARK
            #------------------
            elif soln.Question.scoringMode == ScoringMode.MULTI_ANS_PARTITION:
                soln.Degree = round(PERCENTAGE * FULL_MARK,3)
                studentSheet.TotalMark += round(PERCENTAGE * FULL_MARK,3)
            #------------------
            else:
                soln.Degree = 0
            #------------------
        #------------------
        Soln.objects.bulk_update(SOLNS,'Degree')
        self.useAI(WAITIN_AI_SOLN)
        studentSheet.save()
    #------------------
    def useAI(self,soln:list[Soln]):
        ...
    #------------------
    def mark(self,classRoom,studentSheet:solutionsSheet,soln:Soln,degree:float)->GeneralOutput:
        classRoomAuthenticator = classRoomService(self.Requester)
        output:GeneralOutput = classRoomAuthenticator._RequesterValidation(classRoom,UserPrivileges.CORRECTING_STUDENTS_SOLN)
        if not output["isSuccess"]:
            return output
        studentSheet.LastUpdate = datetime.now()
        soln.correctedBy = self.Requester
        ExamQuestion = Exam_Questions.objects.filter(Exam=solutionsSheet.Exam ,Question=soln.Question).first()
        if not ExamQuestion:
            return GOutput(error={"exam":"exam doesn't include this question"})
        #------------------
        if degree <= ExamQuestion.degree and degree > 0:
            soln.Degree = degree
        elif degree < 0:
            soln.Degree = 0
        else:
            soln.Degree = ExamQuestion.degree
        studentSheet.TotalMark += soln.Degree
        studentSheet.save()
        soln.save()
        return GOutput({"success":"mark saved successfully"})
    #------------------
    def blackListStudent(self,student:IUserHelper,clsRoom:classRoom,exam:Exam,reason:str)->GeneralOutput:
        """kick this student from the current exam session and add him/her to blacklist so they cannot enter it back"""
        classRoomAuthenticator = classRoomService(self.Requester)
        if classRoomAuthenticator._RequesterValidation(clsRoom,UserPrivileges.REMOVE_STUDNET):
            return GOutput(error={"blacklist":"cannot ban the owner"})
        Exam_BlackList.objects.create(
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
    def timeIsUp(self,exam:Exam):
        allSolutionSheets = exam.SolutionSheets.filter(isSubmitted=False)
        currentTime = datetime.now()
        sheetsToUpdate:list[solutionsSheet] = cast(list[solutionsSheet],[])
        for solnSheet in allSolutionSheets:
            solnSheet.SubmitReason = SubmitReason.TIME_ENDED.value
            solnSheet.IsSubmitted = True
            solnSheet.SpecifiedTextReason = f"SYSTEM::exam time ended at {currentTime}"
            sheetsToUpdate.append(solnSheet)
        #------------------
        solutionsSheet.objects.bulk_update(allSolutionSheets,["SubmitReason","IsSubmitted","SpecifiedTextReason"])
    #------------------
#------------------CLASS-ENDED#------------------

class OnlineExam(GeneralExamServices):
    def blackListStudent(self, student: IUserHelper,clsRoom:classRoom ,exam: Exam, reason: str) -> GeneralOutput:
        output = super().blackListStudent(student, clsRoom,exam, reason)
        if not output["isSuccess"]:
            return output
        blackListedSolnSheet = student.solnSheet.filter(student=student).first()
        if not blackListedSolnSheet:
            return GOutput(error={"faild":"for some reason solution sheet is null"})
        if not reason:
            return GOutput(error={"reason":"Text Reason cannot be null"})
        if not student:
            return GOutput(error={"student":"cannot be null"})
        if not exam:
            return GOutput(error={"exam":"cannot be null"})
        blackListedSolnSheet.SubmitReason = SubmitReason.KICKED.value
        blackListedSolnSheet.SpecifiedTextReason = reason
        blackListedSolnSheet.IsSubmitted = True
        blackListedSolnSheet.save()
        return GOutput({"success":"this exam is kicked and blacklisted"})
    #------------------
    def _checkPassKey(self,exam:Exam,passKey:str)->bool:
        passK = exam.PassKey
        if not passK:
            return True
        if not passKey:
            return False
        if passK == passKey:
            return True
        return False
    #------------------
    def _checkGPS(self,exam:Exam,location:Location_Type)->bool:
        examLocation = exam.Locations.filter(Xaxis=location["Xaxis"],Yaxis=location["Yaxis"]).first()
        if exam.Locations.count()==0:
            return True
        #------------------
        if not examLocation:
            return False
        #------------------
        area = examLocation.buildingArea
        r = (area**0.5) * ((2**0.5) / 2) # the radius of the circle that surround the square
        distance = abs(location["Xaxis"] - examLocation.Xaxis) + abs(location["Yaxis"] - examLocation.Yaxis)
        if distance <= r:
            return True
        return False
    #------------------
    def sendCredentials(self, exam: Exam, passKey: str | None = None) -> GeneralOutput[list[QuestionToFront] | None]:
        if not passKey:
            return GOutput(error={"passKey":"cannot be null"})
        isCheck = self._checkPassKey(exam,passKey)
        if not isCheck:
            return GOutput(error={"unauthorized":"cannot access thes exam"})
        #------------------
        return super().sendCredentials(exam, passKey)
    #------------------
    def autoSave(self,exam:Exam,passKey:str,q:Question,student:IUserHelper,ans:str,location:Location_Type)->GeneralOutput:
        if not self._checkPassKey(exam,passKey):
            return GOutput(error={"passKey":"is not correct"})
        #------------------
        if not self._checkGPS(exam,location):
            return GOutput(error={"GPS":"Your location is not correctly in the place it should be"})
        #------------------
        currentSolnSheet = solutionsSheet.objects.filter(exam=exam,student=student,IsSubmitted=False).first()
        if not currentSolnSheet :
            currentSolnSheet = solutionsSheet.objects.create(
                exam=exam,
                student=student
            )
        #------------------
        examStartTime:datetime = exam.StartAt
        duration:int = exam.Duration_min
        finishTime:datetime = examStartTime + timedelta(minutes=duration)
        soln:Soln = currentSolnSheet.Solns.filter(Question=q).first()#type:ignore - because if the currentSolnSheet is not exist , it will be automatically created
        currentTime = datetime.now()
        if finishTime <= currentTime: #if time is up
            currentSolnSheet.SubmitReason = SubmitReason.TIME_ENDED.value
            currentSolnSheet.LastUpdate = currentTime
            currentSolnSheet.IsSubmitted = True
            currentSolnSheet.SpecifiedTextReason = f"SYSTEM::exam time ended at {currentTime}"
            if not soln:
                if not q:
                    return GOutput(error={"question":"cannot be null when creating new solution"})
                newSoln = Soln.objects.create(
                    Question = q,
                    SolvedBy=student,
                    Content=ans,
                    Exam=exam
                )
                Exam_Soln.objects.create(
                    Exam = exam,
                    SolnSheet=currentSolnSheet,
                    soln=newSoln
                )
                # currentSolnSheet.Exam_Soln = newSoln
            #------------------
            else:
                soln.Content = ans
                soln.save()
            return GOutput({"success":"soln saved successfully"})
        #------------------
        if not soln:
            if not q:
                return GOutput(error={"question":"cannot be null when creating new solution"})
            newSoln = Soln.objects.create(
                Question = q,
                SolvedBy=student,
                Content=ans,
                Exam=exam
            )
            # currentSolnSheet. = newSoln
        #------------------
        else:
            soln.Content = ans
            soln.save()
        return GOutput({"success":"soln saved successfully"})
    #------------------
    def submitWithReason(self,exam:Exam,student:IUserHelper,clsRoom,reason:str)->GeneralOutput:
        output = super().blackListStudent(student, clsRoom,exam, reason)
        if not output["isSuccess"]:
            return output
        blackListedSolnSheet = student.solnSheet.filter(student=student).first()
        if not blackListedSolnSheet:
            return GOutput(error={"faild":"for some reason solution sheet is null"})
        if not reason:
            return GOutput(error={"reason":"Text Reason cannot be null"})
        if not student:
            return GOutput(error={"student":"cannot be null"})
        if not exam:
            return GOutput(error={"exam":"cannot be null"})
        blackListedSolnSheet.SubmitReason = SubmitReason.SUBMITTED.value
        blackListedSolnSheet.SpecifiedTextReason = reason
        blackListedSolnSheet.IsSubmitted = True
        blackListedSolnSheet.save()
        return GOutput({"success":"this exam is kicked and blacklisted"})
    #------------------
    def activeUsers(self,exam:Exam)->list[IUserHelper]:
        solnSheets = exam.SolutionSheets.filter(isSubmitted=False).all()
        students = [sheet.Student for sheet in solnSheets]
        return students
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