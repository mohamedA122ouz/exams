from datetime import datetime
from random import choice
from typing import TYPE_CHECKING, Optional
from django.db import models
from django.contrib.auth.models import User
from core.services.types.submitReason import SubmitReason
from core.services.types.modelsHelperTypes import ManyToManyManager
from core.services.types.questionType import QuestionEase, QuestionType, ShareWithEnum
from core.services.types.transactionType import TransactionType
# from django.db.models.fields.related_descriptors import ManyRelatedManager
if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import ManyRelatedManager


class ProfileSettings(models.Model):
    ID = models.AutoField(primary_key=True)
    PreferedLang = models.ForeignKey("supportedLanguages",on_delete=models.CASCADE,null=False,related_name="Profiles")
    User = models.OneToOneField(User,on_delete=models.CASCADE,related_name="Settings")
#------------------
class Year(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    User = models.ForeignKey(User,on_delete=models.CASCADE,related_name="Years")
    Terms : models.Manager["Term"]
    Subjects : models.Manager["Subject"]
#------------------
class Term(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    Year = models.ForeignKey(Year,on_delete=models.CASCADE,related_name="Terms")
    User =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Terms",null=True,default=None)
    Subjects : models.Manager["Subject"]
#------------------
class Subject(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    User =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Subjects",null=True,default=None)
    Term = models.ForeignKey(Term,on_delete=models.CASCADE,related_name="Subjects")
    Year = models.ForeignKey(Year,on_delete=models.CASCADE,related_name="Subjects",default=None,null=True)
    Lectures : models.Manager["Lecture"]
#------------------
class Lecture(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    Subject = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="Lectures")
    User =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Lectures",null=True,default=None)
    Questions : models.Manager["Question"]
#------------------
class Question(models.Model):
    createdAt = models.DateField(null=False)
    ID = models.AutoField(primary_key=True)
    Text_Url = models.CharField(max_length=400)
    Type = models.IntegerField(choices=QuestionType.choices(), default=QuestionType.MCQ_ONE_ANS)
    Ans = models.CharField(max_length=400)
    Lecture = models.ForeignKey(Lecture,on_delete=models.CASCADE,null=True,related_name="Questions")
    InExamCounter = models.IntegerField(default=0,null=False)
    Ease = models.IntegerField(choices=QuestionEase.choices(),default=QuestionEase.EASY)
    Solns:models.Manager["Soln"]
    OwnedBy = models.ForeignKey(User,on_delete=models.CASCADE,related_name="Questions",null=True,default=None)
    Exams:ManyToManyManager["Exam"] # only owner should see this else shouldn't see
#------------------
class Exam(models.Model):
    ID = models.AutoField(primary_key=True)
    PassKey = models.TextField(null=True,blank=True)
    Title = models.TextField(null=True,blank=True)
    CreatedAt = models.DateTimeField(null=False,default=datetime.now())
    Subject = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="Exams")
    Owner =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Exams",null=True,default=None)
    Questions = models.ManyToManyField("Question", through="ExamQuestion", related_name="Exams")
    ClassRooms:ManyToManyManager["classRoom"]
    Solns:models.Manager["Soln"]
    Locations:models.Manager["Location"]
    PreventOtherTabs = models.BooleanField(default=True,null=False)
    Duration_min = models.IntegerField(default=0)
    AutoCorrect = models.BooleanField(default=True)
    QuestionByQuestion = models.BooleanField(default=True)
    ShareWith = models.IntegerField(choices=ShareWithEnum.choices(),default=False)
    AllowDownLoad = models.BooleanField(default=False)
    StartAt = models.DateTimeField(null=True,blank=True)
    EndAt = models.DateTimeField(null=True,blank=True)
    blackListedStudents = models.ManyToManyField(User,through="ExamBlackList",related_name="blackListed")
    if TYPE_CHECKING:
        ExamBlackListTable :ManyRelatedManager["ExamBlackList"]
        solnSheets:ManyRelatedManager["solutionsSheet"]
#------------------
class ExamBlackList(models.Model):
    student = models.ForeignKey(User,models.CASCADE,related_name="ExamBlackListTable")
    exams = models.ForeignKey(Exam,models.CASCADE,related_name="ExamBlackListTable")
    Reason = models.TextField(null=True,blank=True)
#------------------
class ExamQuestion(models.Model):
    Exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    Question = models.ForeignKey(Question, on_delete=models.CASCADE)
    Order = models.IntegerField(default=0)
    sectionName = models.CharField(max_length=150,null=True,blank=True)
#------------------
class Location(models.Model):
    ID = models.AutoField(primary_key=True)
    Xaxis = models.FloatField()
    Yaxis = models.FloatField()
    Exam = models.ForeignKey(Exam,on_delete=models.CASCADE,related_name="Locations")
#------------------
class Soln(models.Model):
    ID = models.AutoField(primary_key=True)
    Question = models.ForeignKey(Question,on_delete=models.CASCADE,related_name="Solns")
    SolvedBy = models.ForeignKey(User,on_delete=models.CASCADE,related_name="Solns")
    Content = models.TextField(null=False,blank=True)
    Exam = models.ManyToManyField(Exam,through="solutionsSheet",related_name="Solns")
    if TYPE_CHECKING:
        solnSheet:ManyRelatedManager["solutionsSheet"]
#------------------
class classRoom(models.Model):
    ID = models.AutoField(primary_key=True)
    OwnedBy = models.OneToOneField(User,on_delete=models.CASCADE,related_name="OwnedClasses",null=False)
    Teacher = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="Teaches",null=True)
    Students = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="StudyAt",null=True)
    Admin = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="Administrate",null=True)
    Attachments = models.FileField(upload_to="uploads/")
    HideFromSearch = models.BooleanField(default=False,null=False)
    Exams = models.ManyToManyField(Exam,through="classRoom_Exam",related_name="ClassRooms")
#------------------
class Attachments(models.Model):
    path = models.FileField(upload_to="uploads/")
    title = models.TextField(null=False,blank=True)
#------------------
class classRoom_Exam(models.Model):
    ID = models.AutoField(primary_key=True)
    Exams = models.ForeignKey(Exam,on_delete=models.CASCADE)
    classRoom = models.ForeignKey(classRoom,on_delete=models.CASCADE)
#------------------
class supportedLanguages(models.Model):
    Name = models.CharField(max_length=2,null=False)
    ID = models.AutoField(primary_key=True)
    Profiles:models.Manager["ProfileSettings"]
#------------------
class solutionsSheet(models.Model):
    LastUpdate = models.DateTimeField(null=False,default=datetime.now())
    SubmitReason = models.IntegerField(choices= SubmitReason.choices())
    SpecifiedTextReason = models.TextField(blank=True,null=False)
    IsSubmitted = models.BooleanField(default=False,null=False)
    TotalMark = models.FloatField(null=False, default=0)
    Ans = models.ForeignKey("Exam",on_delete=models.CASCADE,null=False)
    Exam = models.ForeignKey(Soln,on_delete=models.CASCADE,null=False)
    Student = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name="solnSheet")
#------------------


#------------------MONEY-PART#------------------
class donationTransactions(models.Model):
    Owner = models.ForeignKey(User,on_delete=models.PROTECT,null=False)
    OwnerName = models.CharField(max_length=150,null=False,blank=True)
    Datetime = models.DateTimeField(null=False,default=datetime.now())
    Method = models.CharField(max_length=50,null=False,blank=True)
    Amount = models.DecimalField(null=False,default=0,decimal_places=3,max_digits=10)
    Type = models.IntegerField(choices=TransactionType.choices())
#------------------
class donationBox(models.Model):
    balance = models.DecimalField(null=False,default=0,decimal_places=3,max_digits=10)
    lastTransaction = models.ForeignKey(donationTransactions,on_delete=models.PROTECT)
#------------------
class balance(models.Model):
    Owner = models.OneToOneField(User,on_delete=models.PROTECT,null=False,related_name="Balance")
    Amount = models.DecimalField(null=False,default=0,decimal_places=3,max_digits=10)
#------------------
