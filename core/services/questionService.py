from typing import Any, Optional, cast

from django.forms import model_to_dict

from core.models.Exams_models import  Question
from core.services.types.questionType import QuestionToInsert
from core.services.utils.examParser import toFrontendForm, QuestionFromFront, toDBFromParser
from core.services.types.userType import IUserHelper



class QuestionServices:
    MCQ = 0
    WRITTEN_QUETION = 1
    COMPLEX = 2
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
        questions = self.Owner.Questions.filter(Lecture__ID=lecture_id,ID__gt=last_id).order_by("ID")[:limit].values()
        return list(questions)
    #------------------
    def createQuestion(self,editorInput:Optional[QuestionFromFront],lecture_id:Optional[str]):
        if not editorInput:
            return {"editorInput":"doesn't include data"}
        if not lecture_id:
            return {"lecture_id":"cannot be null"}
        lecture = self.Owner.Lectures.filter(ID=lecture_id).first()
        if not lecture:
            return {"lecture":"lecture not found"}
        if "question" in editorInput:
            return {"editorInput":"editorInput.question cannot be null"}
        if "questionType" in editorInput:
            return {"editorInput":"editorInput.questionType cannot be null"}
        parseResult:QuestionToInsert = toDBFromParser(editorInput)
        q = self.Owner.Questions.create(
            Text_Url=parseResult["question"],
            Type=parseResult["type"],
            Ans=parseResult["ans"],
            IsInAnExam = False,
            soln=None,
            lecture=lecture,
            Ease=parseResult["ease"]
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
            if (result := toDBFromParser(i))["isSuccess"]
        ]
        
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