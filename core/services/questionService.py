from typing import Any, Optional, cast

from core.models.Exams_models import Lecture, Question
from core.services.utils.examParser import ExamAndQuestionParser
from core.services.types.userType import IUserHelper



class QuestionServices:
    MCQ = 0
    WRITTEN_QUETION = 1
    COMPLEX = 2
    def _handleChecking(self,user,text_url:Optional[str],type:Optional[str|int],ans:Optional[str],lecture_id:Optional[str])->dict[str,str]:
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
    def showQuestions(self,user,lecture_id:Optional[int|str],limit:int=100,last_id:int=0)->list[dict[str,Any]]|dict[str,str]:
        user = cast(IUserHelper,user)
        if not lecture_id:
            return {"lecture_id":"cannot be null"}
        questions = user.Questions.filter(lecture__ID=lecture_id,ID__gt=last_id).order_by("ID")[:limit].values()
        return list(questions)
    #------------------
    def createQuestionFromLang(self,user,text_url:Optional[str],ans:Optional[str],lecture_id:Optional[str]):
        user = cast(IUserHelper,user)
        checkingResult = self._handleChecking(user,text_url,"placeHolder",ans,lecture_id)
        if not "success" in checkingResult:
            return checkingResult
        lecture = user.Lectures.filter(ID=lecture_id).first()
        if not lecture:
            return {"lecture":"lecture not found"}
        parseResult = ExamAndQuestionParser(text_url)#type:ignore
        # user.Exams.create(
        #     IsScheduled=False,
        #     Subject=subject,
        #     Questions=,
        #     Settings=,
        #     classRooms=,
        #     solns=,
        # )
        #exam need to be created to continue
        quesitons = [Question(
            Text_Url=result["question"],
            Type=result["questionType"],
            Ans=result["answers"],
            IsInAnExam = False,
            soln=None,
            lecture=lecture,
            Ease=result["ease"]
        ) for result in parseResult]
        user.Questions.bulk_create(quesitons)
    #------------------
    def createQuestion(self,user,text_url:Optional[str],type:Optional[str|int],ans:Optional[str],lecture_id:Optional[str])->dict[str,str]:
        user = cast(IUserHelper,user)
        #text_url is the url of the image on the server
        checkingResult = self._handleChecking(user,text_url,type,ans,lecture_id)
        if not "success" in checkingResult:
            return checkingResult
        lecture = user.Lectures.filter(ID=lecture_id).first()
        if not lecture:
            return {"lecture":"lecture not found"}
        if isinstance(type,str) and not type.isnumeric():
            return {"type":"must be number"}
        elif isinstance(type,str) and type.isnumeric():
            type = int(type)
            if type >= 3:
                type = 2
        #------------------
        q = user.Questions.create(
            Text_Url=text_url,
            Type=int(type),#type:ignore already checked in _handleChecking
            Ans=ans,
            IsInAnExam = False,
            soln=None,
            lecture=lecture
        )
        if not q:
            return {"fail":"creation faild"}
        return {"success":"creation success"}
    #------------------
    def createQuestions(self,user,num:Optional[int|str],text_url:Optional[list[str]],type:Optional[list[str]|list[int]],ans:Optional[list[str]],lecture_id:Optional[list[str]|list[int]])->dict[str,str]:
        user = cast(IUserHelper,user)
        #text_URL the URL FOR IMAGES ON THE SERVER
        if not num:
            return {"num":"questions number cannot be null"}
        elif isinstance(num,str) and not num.isnumeric():
            return {"num":"questions number cannot be a text"}
        qNum = int(num)
        if not text_url:
            return {"text_url":"cannot be null"}
        if not type:
            return {"type":"cannot be null"}
        if not ans:
            return {"ans":"cannot be null"}
        if not lecture_id:
            return {"lecture_id":"cannot be null"}
        if not (len(text_url) == qNum and len(type) == qNum and len(ans) == qNum and len(lecture_id) == qNum):
            return {"num":"some of the parameters doesn't have the same length of the questions number 'num'"}
        QuestionsArr:list[Any] = []
        lectureID = Lecture.objects.filter(Subject__ID__in=lecture_id)
        for itQ in range(0,qNum):
            QuestionsArr.append(Question(
                Text_Url=text_url[itQ],
                Type=type[itQ],
                Ans=ans[itQ],
                lecture=lectureID[itQ],
                IsInAnExam=False,
                User=user
            ))
        #------------------
        items =user.Questions.bulk_create(QuestionsArr)
        if len(items) != qNum:
            return {"fail":"questions list faild to be created"}
        return {"success":"questions list created successfully"}
    #------------------
#------------------CLASS_ENDED#------------------