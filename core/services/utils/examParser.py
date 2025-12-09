import json
from typing import Any, Union, cast

from django.forms import model_to_dict
from core.models.Exams_models import Subject
from core.services.utils.userHelper import IUserHelper
from .questionHelper import AnsParserOutput, ExamAutoGenerator, ExamSetting, QuestionEase
import random

MCQ = 0
WRITTEN_QUETION = 1
COMPLEX = 2
EASY = 0
MEDIUM = 1
HARD = 2
def ExamAndQuestionParser(examText:str)->list[AnsParserOutput]:
    ansList:list[AnsParserOutput] = []
    gForSIMICOLON:list[int] = random.sample(range(999999000,999999999),1)
    _simiColon = f"{gForSIMICOLON[0]}"
    examText = examText.replace("#;",_simiColon)
    counter = 0
    for question in examText.split(';'): # questions
        generateNumber:list[int] = random.sample(range(97890900,97899999),4)
        _tildaSign:str = f"^&*{generateNumber[0]}$%"
        _atSign = f"^&*{generateNumber[1]}$%"
        _randomClass = f"{generateNumber[2]}"
        question = question.replace("#~",_tildaSign)
        question = question.replace("#@",_atSign)
        isMultiChoice = False
        ansString:str = ""
        haveMoreThanOneAns = False
        choices:list[str] = []
        HTMLText = ""
        questionEase = EASY
        for _str in question.split('~'):
            if '@' not in _str:
                HTMLText += f"<p>{_str}</p>"
            else:
                if _str.strip().startswith('CHOICE@') and len(ansString) == 0:
                    choices.append(_str.replace('CHOICE@',''))
                elif _str.strip().startswith('CHOICE@') and len(ansString) != 0:
                    raise Exception("Answer cannot be in the middle of choices it must be at the end")
                elif 'http://' in _str or 'https://' in _str:# if it is a url
                    if _str.strip().startswith('IMAGE@'):
                        HTMLText += f"<img src='{_str.replace('IMAGE@','')}' alt='question Image attachment' />"
                    elif _str.strip().startswith('AUDIO@'):
                        HTMLText += f"<audio src='{_str.replace('AUDIO@','')}' />"
                    elif _str.strip().startswith('VIDEO@'):
                        HTMLText += f"<video src='{_str.replace('VIDEO@','')}' />"
                    elif _str.strip().startswith('YOUTUBE@'):
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
                if _str.strip().startswith("ANS@"):
                    ansString = _str.replace("ANS@","")
                    strArr = ansString.split(',')
                    isMultiChoice = True
                    for item in strArr:
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
                    if easeAsInt > HARD:
                        raise Exception("ease cannot be more than 2 which means HARD")
                    questionEase = easeAsInt
            #------------------
        #------------------
        if haveMoreThanOneAns and isMultiChoice:
            HTMLText += "<p>Choose one or more of the following choices</p>"
            choices = [f"<div><input type='checkbox' value='{key}'>{choice}</div>" for key,choice in enumerate(choices)]
        #------------------
        elif not haveMoreThanOneAns and isMultiChoice:
            HTMLText += "<p>Choose only one of the following choices</p>"
            choices = [f"<div><input type='radio' value='{key}' name='{_randomClass}@ID{counter}'>{choice}</div>" for key,choice in enumerate(choices)]
        #------------------
        elif not isMultiChoice:
            HTMLText += '<textarea placeholder="insert your answer here"></textarea>'
        HTMLText += "".join(choices)
        HTMLText = HTMLText.replace(_atSign,'@')
        HTMLText = HTMLText.replace(_tildaSign,'~')
        HTMLText = HTMLText.replace(_simiColon,';')
        ansList.append({
            'answers':ansString,
            "question":HTMLText,
            'questionType': MCQ if isMultiChoice else WRITTEN_QUETION,
            'ease':questionEase
        })
        counter += 1
    #------------------
    return ansList
#------------------
def autoGeneratorParser(examJson:Union[str,ExamAutoGenerator],user:IUserHelper)->Any:#this should build exam but not it is just checker if all things work
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
    if not "yearName" in examSettings:
        raise "year name doesn't exist"
    if not "subjectName" in examSettings:
        raise "subject name doesn't exist"
    if not "termName" in examSettings:
        raise "term name doesn't exist"
    if not "lectureName" in examSettings:
        raise "lecture name doesn't exist"
    if not "randomization" in examSettings:
        raise "randomization settings doesn't exist"
    examQuestions:list[QuestionEase] = examAGDict['questions']
    if not isinstance(examQuestions,list):
        raise "exam questions is not in list"
    subject = user.Subjects.filter(Name=examSettings['subjectName'],Term__Name=examSettings['termName'],Year__Name=examSettings['yearName']).first()
    if not subject:
        raise Exception(f"cannot find subject: {examSettings} in year:{examSettings['yearName']} and term:{examSettings['termName']}")
    lecture = subject.Lectures.filter(Name=examSettings['lectureName']).first()
    if not lecture:
        raise Exception(f"lecture:{lecture} is not exist")
    easyQuestions = lecture.Questions.filter(Ease=EASY)
    mediumQuestions = lecture.Questions.filter(Ease=MEDIUM)
    hardQuestions = lecture.Questions.filter(Ease=HARD)
    exam = []
    for question in examQuestions:
        if not "count" in question:
            raise Exception("question ease doesn't have a count")
        if not "ease" in question:
            raise Exception("ease level is not exist")
        if question["ease"] == EASY:
            exam+=easyQuestions[:question['count']]
        elif question['ease'] == MEDIUM:
            exam+=mediumQuestions[:question['count']]
        elif question['ease'] == HARD:
            exam+=hardQuestions[:question['count']]
    #------------------
    serialized_exam = [model_to_dict(q) for q in exam]
    if examSettings['randomization']:
        random.shuffle(serialized_exam)
    print(serialized_exam)
    return serialized_exam
#------------------