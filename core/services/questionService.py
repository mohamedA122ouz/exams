from typing import Any, Optional, cast

from django.forms import model_to_dict

from core.models.Exams_models import  Question
from core.services.types.questionType import reverseParserOutput
from core.services.utils.examParser import Qparser, QparserOutput, reverseQParser
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
        questions = self.Owner.Questions.filter(lecture__ID=lecture_id,ID__gt=last_id).order_by("ID")[:limit].values()
        return list(questions)
    #------------------
    def createQuestion(self,editorInput:Optional[QparserOutput],lecture_id:Optional[str]):
        if not editorInput:
            return {"editorInput":"doesn't include data"}
        checkingResult = self._handleChecking("placeHolderText","placeHolder",editorInput["answers"],lecture_id)
        if not "success" in checkingResult:
            return checkingResult
        lecture = self.Owner.Lectures.filter(ID=lecture_id).first()
        if not lecture:
            return {"lecture":"lecture not found"}
        if "question" in editorInput:
            return {"editorInput":"editorInput.question cannot be null"}
        if "questionType" in editorInput:
            return {"editorInput":"editorInput.questionType cannot be null"}
        parseResult:reverseParserOutput = reverseQParser(editorInput)
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
    def createQuestions(self,editorInput:Optional[list[QparserOutput]]):
        if not editorInput:
            return {"editorInput":"cannot be null"}
        checkingResult = self._handleChecking("placeHolderText",editorInput[0]["questionType"],editorInput[0]["answers"],"1")
        if not "success" in checkingResult:
            return checkingResult
        if len(editorInput) == 0:
            return {"editorInput":"doesn't include data have length 0"}
        if "question" in editorInput:
            return {"editorInput":"editorInput.question cannot be null"}
        if "questionType" in editorInput:
            return {"editorInput":"editorInput.questionType cannot be null"}
        
        parseResults:list[reverseParserOutput] = [reverseQParser(i) for i in editorInput]
        questions = [Question(
            OwnedBy=self.Owner,
            Text_Url=q["question"],
            Type=q["type"],
            Ans=q["ans"],
            InExamCounter = 0,
            Lecture_id=q["lecture_id"],#real Bug
            Ease=q["ease"]
        ) for q in parseResults]
        createdItems = self.Owner.Questions.bulk_create(questions)
        if not createdItems or len(createdItems) == 0:
            return {"fail":"creation faild"}
        elif not len(createdItems) == len(questions):
            return {"faild":"something went wrong not all questions created"}
        return {"success":"creation success","createdItems":[model_to_dict(item) for item in createdItems]}
    #------------------
#------------------CLASS_ENDED#------------------