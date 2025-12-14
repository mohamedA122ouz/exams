import json
from typing import Any, Union, cast

from django.forms import model_to_dict
from core.models.Exams_models import Question
from core.services.types.attachmentType import Attachments
from core.services.types.userType import IUserHelper
from ..types.questionType import QparserOutput, ExamAutoGenerator, ExamSetting, QuestionSelector,QuestionEase, QuestionType, reverseParserOutput
import random


def Qparser(examText:str)->list[QparserOutput]:
    """Qparser takes data from database question and convert it to a json that could be send to the frontend 
    | you can use it later on to generate exam directly when user send you text of this language form
    """
    ansList:list[QparserOutput] = []
    gForSIMICOLON:list[int] = random.sample(range(999999000,999999999),1)
    _simiColon = f"{gForSIMICOLON[0]}"
    examText = examText.replace("#;",_simiColon)
    for question in examText.split(';'): # questions
        generateNumber:list[int] = random.sample(range(97890900,97899999),2)
        _tildaSign:str = f"^&*{generateNumber[0]}$%"
        _atSign = f"^&*{generateNumber[1]}$%"
        question = question.replace("$","#$")
        question = question.replace("#@",_atSign)
        question = question.replace("#~",_tildaSign)
        question = question.replace("#","##")
        isMultiChoice = False
        ansString:str = ""
        haveMoreThanOneAns = False
        choices:list[str] = []
        questionText = "" 
        questionItem:QparserOutput = cast(QparserOutput,{})
        attachment:list[Attachments] = []
        attachmentID = 0
        for _str in question.split('~'):
            if '@' not in _str:
                questionText += _str
            else:
                if _str.strip().startswith('CHOICE@') and len(ansString) == 0:
                    isMultiChoice = True
                    choices.append(_str.replace('CHOICE@','').strip())
                #------------------
                elif _str.strip().startswith('CHOICE@') and len(ansString) != 0:
                    raise Exception("Answer cannot be in the middle of choices it must be at the end")
                elif 'http://' in _str or 'https://' in _str:# if it is a url
                    if _str.strip().startswith('IMAGE@'):
                        questionText += f"${attachmentID}"
                        attachment.append({
                            "type":"img",
                            "link":_str.replace('IMAGE@','')
                        })
                        attachmentID+=1
                    #------------------
                    elif _str.strip().startswith('AUDIO@'):
                        questionText += f"${attachmentID}"
                        attachment.append({
                            "type":"audio",
                            "link":_str.replace('AUDIO@','')
                        })
                        attachmentID += 1
                    #------------------
                    elif _str.strip().startswith('VIDEO@'):
                        questionText += f"${attachmentID}"
                        attachment.append({
                            "type":"video",
                            "link":_str.replace('VIDEO@','')
                        })
                        attachmentID += 1
                    #------------------
                    elif _str.strip().startswith('YOUTUBE@'):
                        questionText += f"${attachmentID}"
                        _str = _str.replace('YOUTUBE@','')
                        _str = _str.replace("https://youtu.be/","https://www.youtube.com/embed/")
                        _str = _str.replace("https://www.youtube.com/","https://www.youtube.com/embed/")
                        attachment.append({
                            "type":"youtube",
                            "link":_str
                        })
                        attachmentID += 1
                    else:
                        raise Exception("Cannot have attachments after choice on inside them")
                #------------------
                else:# if the attachment is uploaded to the server
                    if 'IMAGE@' in _str:
                        questionText += f"${attachmentID}"
                        attachment.append({
                            "type":"img",
                            "link":_str.replace('IMAGE@','/static/')
                        })
                        attachmentID += 1
                    #------------------
                    elif 'AUDIO@' in _str:
                        questionText += f"${attachmentID}"
                        attachment.append({
                            "type":"audio",
                            "link":_str.replace('AUDIO@','/static/')
                        })
                        attachmentID += 1
                    #------------------
                    elif 'VIDEO@' in _str and len(choices) > 0:
                        questionText += f"${attachmentID}"
                        attachment.append({
                            "type":"audio",
                            "link":_str.replace('VIDEO@','/static/')
                        })
                        attachmentID += 1
                    #------------------
                #------------------
                
                if _str.strip().startswith("ANS@"):
                    ansString = _str.replace("ANS@","")
                    strArr = ansString.split(',')
                    isMultiChoice = True
                    for item in strArr:
                        item = item.strip()
                        if not item.isnumeric():
                            isMultiChoice = False
                        elif item.isnumeric() and int(item) > len(choices):
                            isMultiChoice = False
                    #------------------
                    if len(strArr) > 1 and isMultiChoice:
                        haveMoreThanOneAns = True
                #------------------
                if _str.strip().startswith("EASE@"):
                    ease = _str.replace("EASE@","")
                    if not ease.isnumeric():
                        raise Exception("ease cannot be string it must be a number")
                    easeAsInt = int(ease)
                    if easeAsInt > QuestionEase.HARD.value:
                        raise Exception("ease cannot be more than 2 which means HARD")
                    questionItem["ease"] = easeAsInt
            #------------------
        #------------------
        if haveMoreThanOneAns and isMultiChoice:
            questionItem["questionType"] = QuestionType.MCQ_MORE_ANS.value
            questionItem["choices"] = choices
        #------------------
        elif not haveMoreThanOneAns and isMultiChoice:
            questionItem["questionType"] = QuestionType.MCQ_ONE_ANS.value
            questionItem["choices"] = choices
        #------------------
        elif not isMultiChoice:
            questionItem["questionType"] = QuestionType.WRITTEN_QUETION.value
            questionItem["choices"] = None
        #------------------
        if isMultiChoice and len(ansString) == 0:
            raise Exception("choices questions cannot be created without any answers")
        questionText = questionText.replace(_atSign,'@')
        questionText = questionText.replace(_tildaSign,'~')
        questionText = questionText.replace(_simiColon,';')
        questionItem["question"] = questionText.strip()
        questionItem["answers"] = ansString.strip()
        questionItem["attachments"] = attachment if len(attachment)>0 else None
        ansList.append(questionItem)
    #------------------
    return ansList
#------------------
def QparserHelper(q:Question)->QparserOutput:
    """Takes Question from database and fix it to allow parser to see question answer"""
    txt = q.Text_Url
    txt += f'~ANS@{q.Ans}'
    return Qparser(txt)[0]
#------------------
def autoGeneratorParser(examJson:Union[str,ExamAutoGenerator],user:IUserHelper)->Any:
    
    examAGDict:ExamAutoGenerator = cast(ExamAutoGenerator,{})
    if isinstance(examJson,str):
        examJson = json.loads(examJson)
    else:
        examAGDict = examJson
    if not "generatorSettings" in examAGDict:
        raise "generator setting not exist"
    if not "questions" in examAGDict:
        raise "exam questions doesn't exist"
    examSettings:ExamSetting = examAGDict['generatorSettings']
    if not "yearID" in examSettings:
        raise "year name doesn't exist"
    if not "subjectID" in examSettings:
        raise "subject name doesn't exist"
    if not "termID" in examSettings:
        raise "term name doesn't exist"
    if not "randomization" in examSettings:
        raise "randomization settings doesn't exist"
    examQuestions:list[QuestionSelector] = examAGDict['questions']
    if not isinstance(examQuestions,list):
        raise "exam questions is not in list"
    subject = user.Subjects.filter(ID=examSettings['subjectID'],Term__Name=examSettings['termID'],Year__Name=examSettings['yearID']).first()
    if not subject:
        raise Exception(f"cannot find subject: {examSettings} in year:{examSettings['yearID']} and term:{examSettings['termID']}")
    exam = []
    for question in examQuestions:
        if not "count" in question:
            raise Exception("question ease doesn't have a count")
        if not "ease" in question:
            raise Exception("ease level is not exist")
        qSet = user.Questions.filter(Ease=question["ease"])
        if not qSet:
            raise Exception("qSet is none or empty")
        exam+=qSet[:question['count']]
    #------------------
    serialized_exam = [model_to_dict(q) for q in exam]
    if examSettings['randomization']:
        random.shuffle(serialized_exam)
    print(serialized_exam)
    return serialized_exam
#------------------
def reverseQParser(jsonItem:QparserOutput)->reverseParserOutput:
    """Takes json from frontend and parser it to allow storing it into database"""
    generateNumber:list[int] = random.sample(range(97890900,97899999),4)
    _simiColon = f"{generateNumber[2]}"
    _tildaSign:str = f"^&*{generateNumber[0]}%"
    _atSign = f"^&*{generateNumber[1]}%"
    _dollar = f"^&*{generateNumber[3]}%"
    jsonItem["question"] = jsonItem["question"].replace("#$",_dollar)
    jsonItem["question"] = jsonItem["question"].replace(";",_simiColon)
    jsonItem["question"] = jsonItem["question"].replace("@",_atSign)
    jsonItem["question"] = jsonItem["question"].replace("~",_tildaSign)
    item:reverseParserOutput = cast(reverseParserOutput,{})
    if jsonItem["attachments"]:
        for i,attachment in enumerate(jsonItem["attachments"]):
            rp = f"~IMAGE@{attachment['link']}" if attachment["type"] == 'img'else f'~{attachment["type"].upper()}@{attachment["link"]}'
            jsonItem["question"] = jsonItem["question"].replace(f'${i}',rp)
        #------------------
    #------------------
    if jsonItem["choices"]:
        jsonItem["question"] = "".join([f'~CHOICE@{choice}' for choice in jsonItem["choices"]])
    #------------------
    jsonItem["question"] = jsonItem["question"].replace(_dollar,"$")
    jsonItem["question"] = jsonItem["question"].replace(_simiColon,"#;")
    jsonItem["question"] = jsonItem["question"].replace(_atSign,"#@")
    jsonItem["question"] = jsonItem["question"].replace(_tildaSign,"#~")
    item["ans"] = jsonItem["answers"]
    item["question"] = jsonItem["question"]
    item["ease"] = jsonItem["ease"]
    item["type"] = jsonItem["questionType"]
    item["lecture_id"] = jsonItem["lecture_id"]
    return item
#------------------