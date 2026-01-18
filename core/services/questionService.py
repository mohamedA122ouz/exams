from datetime import datetime
from typing import Any, Optional, cast

from django.forms import model_to_dict

from core.models.Exams_models import  Lecture, Question
from core.services.types.questionType import QuestionEase, QuestionToFront, QuestionToInsert, GeneralOutput
from core.services.utils.examParser import toFrontendForm, QuestionFromFront, toDBFormParser, toFrontendFormHelper
from core.services.types.userType import IUserHelper
from core.services.utils.generalOutputHelper import GOutput



class QuestionServices:
    
    def __init__(self,user) -> None:
        self.Owner:IUserHelper = cast(IUserHelper,user)
    #------------------
    def _handleChecking(self,text_url:Optional[str],type:Optional[str|int],ans:Optional[str],lecture_id:Optional[str])->dict[str,str]:
        if not self.Owner:
            return {"login":"login is required"}
        if not text_url:
            return {"text_url":"cannot be null"}
        if not type:
            return {"type":"cannot be null"}
        if not ans:
            return {"ans":"cannot be null"}
        if not lecture_id:
            return {"lecture_id":"cannot be null"}
        else:
            return {"success":"nothing wrong"}
    #------------------
    def showQuestions(self,lecture_id:Optional[int|str],limit:int=100,last_id:int=0)->list[dict[str,Any]]|dict[str,str]:
        if not self.Owner:
            return {"login":"login is required"}
        if not lecture_id:
            return {"lecture_id":"cannot be null"}
        questions = self.Owner.Questions.filter(Lecture__ID=lecture_id,ID__gt=last_id).order_by("ID")[:limit].all()
        if not questions:
            return {"questions":"not found"}
        qlist = []
        for q in questions:
            output = toFrontendFormHelper(q)
            if output["isSuccess"] and output["output"]:
                output["output"][0]["ID"] = q.ID
                qlist += output["output"]
        #------------------
        return qlist
    #------------------
    def _validateQuestion(self,editorInput:Optional[QuestionFromFront])->GeneralOutput[Optional[Lecture]]:
        if not editorInput:
            return GOutput(error={"editorInput":"doesn't include data"})
        if not "lecture_id" in editorInput:
            return GOutput(error={"lecture_id":"cannot be null"})
        lecture = self.Owner.Lectures.filter(ID=editorInput["lecture_id"]).first()
        if not lecture:
            return GOutput(error={"lecture":"lecture not found"})
        if not "question" in editorInput:
            return GOutput(error={"editorInput":"editorInput.question cannot be null"})
        if not"questionType" in editorInput:
            return GOutput(error={"editorInput":"editorInput.questionType cannot be null"})
        if not"ease" in editorInput or (editorInput["ease"] > QuestionEase.HARD.value and editorInput["ease"] < QuestionEase.EASY.value):
            return GOutput(error={"editorInput":f"editorInput.ease cannot be null and must be between:{QuestionEase.EASY.value} and {QuestionEase.HARD.value}"})
        if not"attachments" in editorInput:
            return GOutput(error={"editorInput":"editorInput.attachmets cannot be null but can be empty"})
        if not"choices" in editorInput:
            return GOutput(error={"editorInput":"editorInput.choices cannot be null but can be empty"})
        if not "answers" in editorInput or len(editorInput["answers"].strip()) == 0 or not isinstance(editorInput["answers"],str):
            return GOutput(error={"editorInput":"editorInput.answers cannot be null or empty and must be string"})
        #------------------
        return GOutput(lecture)
    #------------------
    def createQuestion(self,editorInput:Optional[QuestionFromFront]):
        validateOutput = self._validateQuestion(editorInput)
        if not validateOutput["isSuccess"]:
            return validateOutput
        lecture:Lecture = cast(Lecture, validateOutput["output"])
        parseResult:GeneralOutput[QuestionToInsert] = toDBFormParser(editorInput) #type:ignore Validated already from valdiator
        if not parseResult["isSuccess"]:
            return {"faild":parseResult["output"]}
        #------------------
        correctResult = parseResult["output"]
        q = self.Owner.Questions.create(
            createdAt=datetime.now(),
            Text_Url=correctResult["question"],
            Type=correctResult["type"],
            Ans=correctResult["ans"],
            InExamCounter = 0,
            Lecture=lecture,
            Ease=correctResult["ease"]
        )
        if not q:
            return {"fail":"creation faild"}
        return {"success":"creation success","createdItems":model_to_dict(q)}
    #------------------
    def createQuestions(self,editorInput:Optional[list[QuestionFromFront]]):
        if not editorInput:
            return {"editorInput":"cannot be null"}
        if len(editorInput) == 0:
            return {"editorInput":"cannot be empty"}
        checkingResult = self._handleChecking("placeHolderText",editorInput[0]["questionType"],editorInput[0]["answers"],"1")
        if not "success" in checkingResult:
            return checkingResult
        if "question" in editorInput:
            return {"editorInput":"editorInput.question cannot be null"}
        if "questionType" in editorInput:
            return {"editorInput":"editorInput.questionType cannot be null"}
        
        faildToCreate = []
        parseResults: list[QuestionToInsert] = [
            result["output"]
            for i in editorInput
            if (result := toDBFormParser(i))["isSuccess"]
        ] #type:ignore if success then the output is always not None
        
        questions: list[Question] = []
        user_lectures = set(
            int(lec)
            for lec in self.Owner.Lectures.values_list("ID", flat=True)
        )
        for q in parseResults:
            if isinstance(q["lecture_id"],str) and not q["lecture_id"].isdigit():
                faildToCreate.append(q)
                continue
            #------------------
            if not int(q["lecture_id"]) in user_lectures:
                faildToCreate.append(q)
                continue
            #------------------
            questions.append(
                Question(
                    OwnedBy=self.Owner,
                    Text_Url=q["question"],
                    Type=q["type"],
                    Ans=q["ans"],
                    InExamCounter=0,
                    Lecture_id=q["lecture_id"],
                    Ease=q["ease"],
                )
            )
        #------------------
        createdItems = self.Owner.Questions.bulk_create(questions)
        if len(faildToCreate) > 0 and len(faildToCreate) < len(parseResults):
            return {"success":"not all you job is create but some of them it you may entered a wrong lecture ids","notCreated":faildToCreate}
        if len(faildToCreate) > 0 and len(faildToCreate) == len(parseResults):
            return {"faild":"you may entered a wrong lecture ids","notCreated":faildToCreate}
        if not createdItems or len(createdItems) == 0:
            return {"fail":"creation faild"}
        elif not len(createdItems) == len(questions):
            return {"faild":"something went wrong not all questions created"}
        return {"success":"creation success","createdItems":[model_to_dict(item) for item in createdItems]}
    #------------------
#------------------CLASS_ENDED#------------------