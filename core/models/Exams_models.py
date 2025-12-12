from random import choice
from django.db import models
from django.contrib.auth.models import User
from core.services.types.questionType import QuestionEase, QuestionType




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
    lecture = models.ForeignKey(Lecture,on_delete=models.CASCADE,related_name="Questions")
    IsInAnExam = models.BooleanField()
    Ease = models.IntegerField(choices=QuestionEase.choices(),default=QuestionEase.EASY)
    soln:models.Manager["soln"]
    User =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Questions",null=True,default=None)
    Exams:models.Manager["Exam"] # only owner should see this else shouldn't see
#------------------
class Setting(models.Model):
    ID = models.AutoField(primary_key=True)
    ExamInterval = models.TimeField()
    AutoCorrect = models.BooleanField(default=True)
    QuestionByQuestion = models.BooleanField(default=True)
    TrackSolutions = models.BooleanField(default=True)
    Public = models.BooleanField(default=False)
    AllowDownLoad = models.BooleanField(default=False)
#------------------

class Exam(models.Model):
    ID = models.AutoField(primary_key=True)
    IsScheduled = models.BooleanField()
    Subject = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="Exams")
    User =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Exams",null=True,default=None)
    Questions = models.ManyToManyField("Question", through="ExamQuestion", related_name="Exams")
    Settings = models.ForeignKey(Setting, on_delete=models.CASCADE)
    classRooms:models.Manager["classRoom"]
    solns:models.Manager["soln"]
#------------------
class ExamQuestion(models.Model):
    Exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    Question = models.ForeignKey(Question, on_delete=models.CASCADE)
    Order = models.IntegerField(default=0)
#------------------

class soln(models.Model):
    ID = models.AutoField(primary_key=True)
    Exam = models.ForeignKey(Exam,on_delete=models.CASCADE,related_name="Solns")
    Question = models.ForeignKey(Question,on_delete=models.CASCADE,related_name="Solns")
    User = models.ForeignKey(User,on_delete=models.CASCADE,related_name="Solns")
#------------------
class classRoom(models.Model):
    ID = models.AutoField(primary_key=True)
    Creator = models.ForeignKey(User,on_delete=models.CASCADE,related_name="classRoomsOwner",null=False)
    Students = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="classRoomsMember",null=True)
    Admin = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="Admin",null=True)
    attachments = models.FileField(upload_to="uploads/")
    allowThirdPartySeen = models.BooleanField(default=False,null=False)
#------------------