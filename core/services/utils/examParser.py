import json
from typing import Any, Optional, Union, cast

from django.forms import model_to_dict
from core.models.Exams_models import Question
from core.services.types.attachmentType import Attachments
from core.services.types.userType import IUserHelper
from ..types.questionType import AutoGenExamSetting, QparserOutput, ExamAutoGenerator, QuestionSelector,QuestionEase, QuestionType, parserOutput, reverseParserOutput
import random


def Qparser(examText:str)->parserOutput[Optional[list[QparserOutput]]]:
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
                    return {
                            "error":{"examText":"Answer cannot be in the middle of choices it must be at the end"},
                            "isSuccess":False,
                            "output":None
                        }
                #------------------
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
                        return {
                            "error":{"examText":"Cannot have attachments after choice on inside them"},
                            "isSuccess":False,
                            "output":None
                        }
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
                        return {
                            "error":{"examText":"ease cannot be string it must be a number"},
                            "isSuccess":False,
                            "output":None
                        }
                    #------------------
                    easeAsInt = int(ease)
                    if easeAsInt > QuestionEase.HARD.value:
                        return {
                            "error":{"examText":"ease cannot be more than 2 which means HARD"},
                            "isSuccess":False,
                            "output":None
                        }
                    #------------------
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
    return {
        "error":None,
        "isSuccess":True,
        "output":ansList
    }
#------------------
def QparserHelper(q:Question)->parserOutput[Optional[QparserOutput]]:
    """Takes Question from database and fix it to allow parser to see question answer"""
    txt = q.Text_Url
    txt += f'~ANS@{q.Ans}'
    items =  Qparser(txt)
    if items["output"] and len(items["output"]) > 0:
        item = items["output"][0]
        return {
            "error":items["error"],
            "isSuccess":items["isSuccess"],
            "output":item
        }
    #------------------
    return {
        "error":items["error"],
        "isSuccess":items["isSuccess"],
        "output":None
    }
#------------------
def autoGeneratorParser(examJson:Union[str,ExamAutoGenerator],user:IUserHelper)->parserOutput[Optional[list[dict[str,Any]]]]:
    
    examAGDict:ExamAutoGenerator = cast(ExamAutoGenerator,{})
    if isinstance(examJson,str):
        examJson = json.loads(examJson)
    else:
        examAGDict = examJson
    if not "generatorSettings" in examAGDict:
        return {
            "error":{"generatorSettings":"generator setting not exist"},
            "isSuccess":False,
            "output":None
        }
    #------------------
    if not "questions" in examAGDict:
        return {
            "error":{"questions":"exam questions doesn't exist"},
            "isSuccess":False,
            "output":None
        }
    #------------------
    examSettings:AutoGenExamSetting = examAGDict['generatorSettings']
    if not "yearID" in examSettings:
        return {
            "error":{"generatorSettings":"generatorSettings.yearID doesn't exist"},
            "isSuccess":False,
            "output":None
        }
    #------------------
    if not "subjectID" in examSettings:
        return {
            "error":{"generatorSettings":"generatorSettings.subjectID doesn't exist"},
            "isSuccess":False,
            "output":None
        }
    #------------------
    if not "termID" in examSettings:
        return {
            "error":{"generatorSettings":"generatorSettings.termID doesn't exist"},
            "isSuccess":False,
            "output":None
        }
    #------------------
    if not "randomization" in examSettings:
        return {
            "error":{"generatorSettings":"generatorSettings.randomization settings doesn't exist"},
            "isSuccess":False,
            "output":None
        }
    #------------------
    examQuestions:list[QuestionSelector] = examAGDict['questions']
    if not isinstance(examQuestions,list):
        raise "exam questions is not in list"
    subject = user.Subjects.filter(ID=examSettings['subjectID'],Term__ID=examSettings['termID'],Year__ID=examSettings['yearID']).first()
    if not subject:
        return {
            "error":{"subject":f"cannot find subject: {examSettings} in year:{examSettings['yearID']} and term:{examSettings['termID']}"},
            "isSuccess":False,
            "output":None
        }
    #------------------
    exam = []
    for i,question in enumerate(examQuestions):
        if not "count" in question:
            return {
                "error":{"questions":f"questions[{i}].count doesn't have a value (you must count the selection)"},
                "isSuccess":False,
                "output":None
            }
        if not "ease" in question:
            return {
                "error":{"questions":f"questions[{i}].ease doesn't have a value"},
                "isSuccess":False,
                "output":None
            }
        qSet = user.Questions.filter(Ease=question["ease"])
        if not qSet:
            return {
                "error":{"qSet":f"is none or empty"},
                "isSuccess":False,
                "output":None
            }
        exam+=qSet[:question['count']]
    #------------------
    serialized_exam = [model_to_dict(q) for q in exam]
    if examSettings['randomization']:
        random.shuffle(serialized_exam)
    print(serialized_exam)
    return {
        "error":None,
        "isSuccess":True,
        "output":serialized_exam
    }
#------------------
def reverseQParser(jsonItem:QparserOutput)->parserOutput[reverseParserOutput]:
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
    return {
        "error":None,
        "isSuccess":True,
        "output":item
    }
#------------------