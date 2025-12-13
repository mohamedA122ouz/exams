import pytest
import json
from core.controllers.API_v0 import createQuestions
from core.models.Exams_models import Lecture, Subject, Term, Year
from core.services.questionService import QuestionServices
from core.services.types.questionType import QuestionEase, QuestionType
from core.services.utils.examParser import Qparser, QparserType
from django.contrib.auth.models import User

def test_one_ans_choices():
    question = "QUESTION1$$~CHOICE@1~CHOICE@2~CHOICE@3~ANS@0"
    data:list[QparserType] = Qparser(question)
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
    data:list[QparserType] = Qparser(question)
    assert data[0]["questionType"] == QuestionType.MCQ_MORE_ANS.value 
    assert data[0]["choices"] and len(data[0]["choices"]) > len(data[0]["answers"].split(','))
    assert '@' in data[0]["question"]
    assert '~' in data[0]["question"]
    assert data[0]["attachments"] == None
    assert data[0]["answers"] == '0,2'
    assert len(data[0]["choices"]) == 4
    assert data[0]["choices"][0] == '1'
#------------------
@pytest.mark.django_db
def test_createQuestion():
    year = Year.objects.create(Name="year1")
    year = Term.objects.create(Name="term1")
    subject = Subject.objects.create(Name="lec1",)
    lecture = Lecture.objects.create(Name="lec1")
    user = User.objects.create_user(username="test",password="Password@123",email="test@gmail.com",last_name="lastName Test",first_name="FirstTest")
    # user = User.objects.filter(email='test@gmail.com').first()
    question:QparserType = {
        "answers":"52",
        "attachments":None,
        "choices":[],
        "question":"test question",
        "ease":QuestionEase.EASY.value,
        "questionType":QuestionType.WRITTEN_QUETION.value
    }
    qService = QuestionServices()
    createdItems = qService.createQuestion(user,question,"1")
    assert "success" in createdItems
#------------------