from typing import Any, Optional, cast

from core.models.Exams_models import Lecture, Question
from core.services.userHelper import IUserHelper
import random

"""
A parser need to be implemented here so the question could be more complicated
> allow include attachments:Image,Audio,Video,URL-> for youtube or other
> allow changing the orientaion of the question and the attachments allowing the question to on top or vice versa
> for choose question allow the computer understand the correct question and generate the choices from the ans

------SMALL EXAMLE OF WHAT THE TEXT SHOULD LOOK LIKE------
EXAMPLE:"look at the question and ans~IMAGE@NAME|URL~what do you found interesting in this image?"
DESCRIPTION: question followed by the image then other question

question
------IMAGE------
question_continue


PROBLEM:Must a void using @ in the regular question or made up a replacer in regular text like #@ and #~;

solution: generate a sequence of number and special chars but just a random sequence and replace #@ then after replacing all @ then restore replace the random sequence with @
so lets say that the question have the following text

> "hello#~ are you there~IMAGE@https://test.com/image~what is the name of thie sign '#@'"
parse should do the following:
1. generate number Sequenece like 78$451%88
2. save it like _tilda = $78451%
3. replace all #~ with the sequenence
4. process all ~ signs as intended
5. replace the random sequence store within the var _tilda with the ~ sign
samething as ~ with @
"""



class QuestionServices:
    def _parser_text_url(self,text:str)->str:
        generateNumber:list[int] = random.sample(range(99,999),2)
        _tildaSign:str = "^"+str(generateNumber[0])+"$%"
        _atSign = "^"+str(generateNumber[1]) +"$%"
        text = text.replace("#~",_tildaSign)
        text = text.replace("#@",_atSign)
        HTMLText = ""
        for _str in text.split('~'):
            if '@' not in _str:
                HTMLText += f"<p>{_str}</p>"
            else:
                if 'http://' in _str or 'https://' in _str:# if it is a url
                    if 'IMAGE' in _str:
                        HTMLText += f"<img src='{_str.replace('IMAGE@','')}' alt='question Image attachment' />'"
                    elif 'AUDIO' in _str:
                        HTMLText += f"<audio src='{_str.replace('AUDIO@','')}' />"
                    elif 'VIDEO' in _str:
                        HTMLText += f"<video src='{_str.replace('VIDEO@','')}' />"
                #------------------
                else:# if the attachment is uploaded to the server
                    if 'IMAGE' in _str:
                        HTMLText += f"<img src='{_str.replace('IMAGE@','/static/')} alt='question Image attachment' />'"
                    elif 'AUDIO' in _str:
                        HTMLText += f"<audio src='{_str.replace('AUDIO@','/static/')}' />"
                    elif 'VIDEO' in _str:
                        HTMLText += f"<video src='{_str.replace('VIDEO@','/static/')}' />"
                #------------------
            #------------------
        #------------------
        return HTMLText
    #------------------
    def showQuestions(self,user,lecture)->list[dict[str,Any]]|dict[str,str]:
        user = cast(IUserHelper,user)
        if not lecture:
            return {"lecture":"cannot be null"}
        questions = user.Questions.filter(lecture__ID=lecture).values()
        return list(questions)
    #------------------
    def createQuestion(self,user,text_url:Optional[str],type:Optional[str|int],ans:Optional[str],lecture_id:Optional[str])->dict[str,str]:
        user = cast(IUserHelper,user)
        #text_url is the url of the image on the server
        if not text_url:
            return {"text_url":"cannot be null"}
        if not type:
            return {"type":"cannot be null"}
        if not ans:
            return {"ans":"cannot be null"}
        if not lecture_id:
            return {"lecture_id":"cannot be null"}
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
            Type=int(type),
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
#------------------CLASS_ENDED#------------------