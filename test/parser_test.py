import pytest
import json
from core.services.types.questionType import AnsParserOutput, QuestionType
from core.services.utils.examParser import ExamAndQuestionParser

def test_one_ans_choices():
    question = "QUESTION1$$~CHOICE@1~CHOICE@2~CHOICE@3~ANS@2"
    data:list[AnsParserOutput] = ExamAndQuestionParser(question)
    assert data[0]["questionType"] == QuestionType.MCQ_ONE_ANS.value and data[0]["choices"] and len(data[0]["choices"]) > 0
#------------------
def test_many_ans_choices():
    question = """
    QUESTION CHOICE#@ ## #~
    ~CHOICE@1
    ~CHOICE@2
    ~CHOICE@3
    ~CHOICE@4
    ~ANS@0,2
    """
    data:list[AnsParserOutput] = ExamAndQuestionParser(question)
    assert data[0]["questionType"] == QuestionType.MCQ_MORE_ANS.value 
    assert data[0]["choices"] and len(data[0]["choices"]) > len(data[0]["answers"].split(','))
    assert '@' in data[0]["question"]
    assert '~' in data[0]["question"]
    assert data[0]["attachments"] == None
    assert data[0]["answers"] == '0,2'
    assert len(data[0]["choices"]) == 4
    assert data[0]["choices"][0] == '1'
#------------------