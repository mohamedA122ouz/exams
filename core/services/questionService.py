from typing import Any, Optional, cast

from core.models.Exams_models import Lecture, Question
from core.services.utils.questionHelper import AnsParserOutput
from core.services.utils.userHelper import IUserHelper
import random



class QuestionServices:
    MCQ = 0
    WRITTEN_QUETION = 1
    COMPLEX = 2
    def _parser_text_url(self,question:Question)->str:
        text:str = question.Text_Url
        generateNumber:list[int] = random.sample(range(97890900,97899999),3)
        _tildaSign:str = f"^&*{generateNumber[0]}$%"
        _atSign = f"^&*{generateNumber[1]}$%"
        _randomClass = f"{generateNumber[2]}"
        text = text.replace("#~",_tildaSign)
        text = text.replace("#@",_atSign)
        choices:list[str] = []
        HTMLText = ""
        for _str in text.split('~'):
            if '@' not in _str:
                HTMLText += f"<p>{_str}</p>"
            else:
                if 'CHOICE@' in _str and question.Type == self.MCQ:
                    choices.append(_str.replace('CHOICE@',''))
                elif 'http://' in _str or 'https://' in _str:# if it is a url
                    if 'IMAGE@' in _str:
                        HTMLText += f"<img src='{_str.replace('IMAGE@','')}' alt='question Image attachment' />"
                    elif 'AUDIO@' in _str:
                        HTMLText += f"<audio src='{_str.replace('AUDIO@','')}' />"
                    elif 'VIDEO@' in _str:
                        HTMLText += f"<video src='{_str.replace('VIDEO@','')}' />"
                    elif 'YOUTUBE@' in _str:
                        _str = _str.replace('YOUTUBE@','')
                        _str = _str.replace("https://youtu.be/","https://www.youtube.com/embed/")
                        _str = _str.replace("https://www.youtube.com/","https://www.youtube.com/embed/")
                        HTMLText += f"""<iframe width="560" height="315" src="{_str}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>"""
                #------------------
                else:# if the attachment is uploaded to the server
                    if 'IMAGE@' in _str:
                        HTMLText += f"<img src='{_str.replace('IMAGE@','/static/')} alt='question Image attachment' />"
                    elif 'AUDIO@' in _str:
                        HTMLText += f"<audio src='{_str.replace('AUDIO@','/static/')}' />"
                    elif 'VIDEO@' in _str:
                        HTMLText += f"<video src='{_str.replace('VIDEO@','/static/')}' />"
                #------------------
            #------------------
        #------------------
        if ',' in cast(str,question.Ans) and question.Type == self.MCQ:
            HTMLText += "<p>Choose one or more of the following choices</p>"
            choices = [f"<div><input type='checkbox' value='{key}'>{choice}</div>" for key,choice in enumerate(choices)]
        #------------------
        elif question.Type == self.MCQ:
            HTMLText += "<p>Choose only one of the following choices</p>"
            choices = [f"<div><input type='radio' value='{key}' name='{_randomClass+str(question.ID)}'>{choice}</div>" for key,choice in enumerate(choices)]
        #------------------
        elif question.Type == self.WRITTEN_QUETION:
            HTMLText += '<textarea placeholder="insert your answer here"></textarea>'
        HTMLText += "".join(choices)
        HTMLText = HTMLText.replace(_atSign,'@')
        HTMLText = HTMLText.replace(_tildaSign,'~')
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