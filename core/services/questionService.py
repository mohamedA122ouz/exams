from datetime import datetime
from typing import Any, Optional, cast

from django.forms import model_to_dict

from core.models.Exams_models import  Lecture, Question
from core.services.types.questionType import QuestionEase, QuestionToFront, QuestionToInsert, GeneralOutput
from core.models.Model_serializers.questionType_serializer import QuestionFromFront_Serializer
from core.services.utils.examParser import toFrontendForm, QuestionFromFront, toDBFormParser, toFrontendFormHelper
from core.services.types.userType import IUserHelper
from core.services.utils.generalOutputHelper import GOutput



class QuestionServices:
    
    def __init__(self,user) -> None:
        self.Owner:IUserHelper = cast(IUserHelper,user)
    #---------------
    def showQuestions(self,lecture_id:Optional[int|str],limit:int=100,last_id:int=0)->list[dict[str,Any]]|dict[str,str]:
        if not self.Owner:
            return {"login":"login is required"}
        if not lecture_id:
            return {"lecture_id":"cannot be null"}
        questions = self.Owner.Questions.filter(Lecture__ID=lecture_id,ID__gt=last_id).order_by("ID")[:limit]
        if not questions:
            return {"questions":"not found"}
        qlist = []
        for q in questions:
            output = toFrontendFormHelper(q)
            if output["isSuccess"] and output["output"]:
                output["output"][0]["ID"] = q.ID
                qlist += output["output"]
        #---------------
        return qlist
    #---------------
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
        #---------------
        return GOutput(lecture)
    #---------------
    def createQuestion(self,editorInput:Optional[QuestionFromFront]):
        validateOutput = self._validateQuestion(editorInput)
        if not validateOutput["isSuccess"]:
            return validateOutput
        lecture:Lecture = cast(Lecture, validateOutput["output"])
        parseResult:GeneralOutput[QuestionToInsert] = toDBFormParser(editorInput) #type:ignore Validated already from valdiator
        if not parseResult["isSuccess"]:
            return {"failed":parseResult["output"]}
        #---------------
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
            return {"fail":"creation failed"}
        return {"success":"creation success","createdItems":model_to_dict(q)}
    #---------------
    def createQuestions(self,editorInput:Optional[list[QuestionFromFront]])->GeneralOutput:
        try:
            if not editorInput:
                return GOutput(error={"editorInput":"cannot be null"})
            #---------------
            newInput = [cast(QuestionFromFront,toDBFormParser(i)["output"]) for i in editorInput]
            if len(editorInput) != len(newInput):
                return GOutput(error={"parserError":"cannot be null"})
            #---------------
            serialized = QuestionFromFront_Serializer(data=newInput,many=True)
            if serialized.is_valid():
                serialized.save(OwnedBy=self.Owner)
            else:
                raise Exception("not vaild from serializers")
            return GOutput(error={"success":"created successfully"})
        except Exception as e:
            print(e)
            return GOutput(error={"fail":"please check admin"})
        #---------------
    #---------------
#---------------CLASS_ENDED#---------------