from datetime import datetime
from random import choice
from django.db import models
from django.contrib.auth.models import User
from core.services.types.modelsHelperTypes import ManyToManyManager
from core.services.types.questionType import QuestionEase, QuestionType, ShareWithEnum


class ProfileSettings(models.Model):
    ID = models.AutoField(primary_key=True)
    PreferedLang = models.TextField(default='EN',null=False)
    User = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="Settings")

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
    ID = models.AutoField(primary_key=True)
    Text_Url = models.CharField(max_length=400)
    Type = models.IntegerField(choices=QuestionType.choices(), default=QuestionType.MCQ_ONE_ANS)
    Ans = models.CharField(max_length=400)
    Lecture = models.ForeignKey(Lecture,on_delete=models.CASCADE,related_name="Questions")
    InExamCounter = models.IntegerField(default=0,null=False)
    Ease = models.IntegerField(choices=QuestionEase.choices(),default=QuestionEase.EASY)
    Solns:models.Manager["Soln"]
    OwnedBy = models.ForeignKey(User,on_delete=models.CASCADE,related_name="Questions",null=True,default=None)
    Exams:ManyToManyManager["Exam"] # only owner should see this else shouldn't see
#------------------
class Exam(models.Model):
    ID = models.AutoField(primary_key=True)
    Title = models.TextField(null=True,blank=True)
    CreatedAt = models.DateTimeField(null=False,default=datetime.now())
    Subject = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="Exams")
    Owner =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Exams",null=True,default=None)
    Questions = models.ManyToManyField("Question", through="ExamQuestion", related_name="Exams")
    ClassRooms:ManyToManyManager["classRoom"]
    Solns:models.Manager["Soln"]
    Settings:models.Manager["Settings"]
#------------------
class ExamQuestion(models.Model):
    Exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    Question = models.ForeignKey(Question, on_delete=models.CASCADE)
    Order = models.IntegerField(default=0)
#------------------
class Settings(models.Model):
    Locations:models.Manager["Location"]
    ID = models.AutoField(primary_key=True)
    PreventOtherTabs = models.BooleanField(default=True,null=False)
    Duration_min = models.IntegerField(default=0)
    AutoCorrect = models.BooleanField(default=True)
    QuestionByQuestion = models.BooleanField(default=True)
    ShareWith = models.IntegerField(choices=ShareWithEnum.choices(),default=False)
    AllowDownLoad = models.BooleanField(default=False)
    StartAt = models.DateTimeField(null=True,blank=True)
    EndAt = models.DateTimeField(null=True,blank=True)
    Exam = models.OneToOneField(Exam,null=True,blank=True,related_name="Settings",on_delete=models.CASCADE)
#------------------
class Location(models.Model):
    ID = models.AutoField(primary_key=True)
    Xaxis = models.FloatField()
    Yaxis = models.FloatField()
    Settings = models.ForeignKey(Settings,on_delete=models.CASCADE,related_name="Locations")
#------------------
class Soln(models.Model):
    ID = models.AutoField(primary_key=True)
    Exam = models.ForeignKey(Exam,on_delete=models.CASCADE,related_name="Solns")
    Question = models.ForeignKey(Question,on_delete=models.CASCADE,related_name="Solns")
    SolvedBy = models.ForeignKey(User,on_delete=models.CASCADE,related_name="Solns")
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
class classRoom_Exam(models.Model):
    ID = models.AutoField(primary_key=True)
    Exams = models.ForeignKey(Exam,on_delete=models.CASCADE)
    classRoom = models.ForeignKey(classRoom,on_delete=models.CASCADE)
#------------------