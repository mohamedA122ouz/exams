import json
from pathlib import Path
from typing import List, Mapping, cast
from django.test import TestCase,TransactionTestCase, Client
from unittest import TestCase as NO_Rollback_TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from pydantic import TypeAdapter
from core.services.questionService import QuestionServices
from core.models.Exams_models import Lecture, Year, Term, classRoom, Subject
from core.services.types.examTypes import examRequest
from core.services.types.questionType_serializer import QuestionFromFront_Serializer
from core.services.utils.classRoomTypes import ClassRoomFromFrontend
from .types import User_type
from rest_framework.serializers import ListSerializer


class APIv0Tests(TransactionTestCase):
    reset_sequences = False
    @classmethod
    def setUpClass(cls):
        """Created once at the start of the database session."""
        cls.payloadDir = Path(__file__).parent / "payload"
        users_dir = cls.payloadDir / "usersCredentials.json"
        with open(users_dir) as file:
            fileJson = file.read()
            all_users = TypeAdapter(List[User_type])
            users:list[User_type] = all_users.validate_json(fileJson)
            for user in users:
                User.objects.create_user(**user.model_dump())
            #---------------
        #---------------
        # Memory-only storage for IDs to pass between functions
        cls.user = User.objects.filter(username="Mohamed.Azouz").first()
        cls.year_id = None
        cls.term_id = None
        cls.classroom_id = None
        cls.subject_id = None
        cls.lec_id = None
    #---------------
    def _fixture_teardown(self):
        ...
    #---------------
    def setUp(self):
        """Runs before every test: ensures login and fresh client."""
        self.client = Client()
        if not self.user:
            raise ValueError("cannot have user not logged in")
        self.client.force_login(self.user)
    #---------------
    # --- ORDERED STEP 1: YEAR ---
    def test_01_create_year(self):
        data = {"name": "2024"}
        response = self.client.post(reverse('v0_createYear'), 
                                    data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Save to class so test_02 can see it
        year = Year.objects.get(Name="2024")
        type(self).year_id = year.ID
    #---------------
    # --- ORDERED STEP 2: TERM ---
    def test_02_create_term(self):
        # We manually re-create the Year because test_01 rolled back the DB
        year = Year.objects.filter(ID=self.year_id, Name="2024", User=self.user).first()
        if not year:
            raise Exception("year not found")
        data = {"name": "Term 1", "year_id": year.ID}
        response = self.client.post(reverse('v0_createTerm'), 
                                    data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        term = Term.objects.get(Name="Term 1")
        type(self).term_id = term.ID
    #---------------
    # --- ORDERED STEP 4: SUBJECT ---
    def test_03_create_subject(self):
        # Re-create parents in DB for the API to find them
        data = {
            "year_id": self.year_id,
            "term_id": self.term_id,
            "name": "Math"
        }
        response = self.client.post(reverse('v0_createSubject'), 
                                    data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        sub = Subject.objects.get(Name="Math")
        type(self).subject_id = sub.ID
    #---------------
    def test_04_create_lecture(self):
        # Re-create parents in DB for the API to find them
        data = {
            "subject_id": self.subject_id,
            "name": "lec1"
        }
        response = self.client.post(reverse('v0_createLectures'), 
                                    data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        lec = Lecture.objects.get(Name="lec1")
        type(self).lec_id = lec.ID
    #---------------
    # --- ORDERED STEP 5: CLASSROOM ---
    def test_05_create_classroom(self):
        data: ClassRoomFromFrontend = {
            "HideFromSearch":False,
            "PaymentAccessMaxCount":0,
            "paymentAmount":0,
            "PaymentExpireInterval_MIN":0,
            "title":"Room1"
        }
        response = self.client.post(reverse('v0_createClassRoom'), 
                                    data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        cr = classRoom.objects.get(Title="Room1")
        type(self).classroom_id = cr.ID
    #---------------
    def test_06_createQBank(self):
        res = None
        with open(self.payloadDir / "QBank.json") as fileStream:
            fileContent = fileStream.read()
            res = self.client.post(reverse("v0_createQuestions"),data=fileContent, content_type='application/json')
            self.assertEqual(res.status_code,200)
        #---------------
    #---------------
    def test_07_createExam(self):
        res = None
        with open(self.payloadDir / "createExam.json") as fileStream:
            fileContent = fileStream.read()
            res = self.client.post(reverse("v0_createExam"),data=fileContent, content_type='application/json')
        #---------------
        self.assertEqual(res.status_code,200)
    #---------------
    def test_08_show_exam_from_Other_User(self):
        user2 = User.objects.filter(username="user2").first()
        if not user2:
            raise ValueError("cannot have user2 as null")
        #---------------
        self.client.force_login(user2)
        res = self.client.get(reverse("v0_showExamOutOfCommit"),data={'exam_id': 1})
        self.assertEqual(res.status_code,404)
    #---------------
#---------------