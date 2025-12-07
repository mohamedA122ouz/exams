from random import choice
from django.db import models
from django.contrib.auth.models import User




class Year(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    User = models.ForeignKey(User,on_delete=models.CASCADE,related_name="Years")
    Terms = models.Manager["Term"]
    Subjects = models.Manager["Subject"]
#------------------

class Term(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    Year = models.ForeignKey(Year,on_delete=models.CASCADE,related_name="Terms")
    User =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Terms",null=True,default=None)
    Subjects = models.Manager["Subject"]
#------------------

class Subject(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    User =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Subjects",null=True,default=None)
    Term = models.ForeignKey(Term,on_delete=models.CASCADE,related_name="Subjects")
    Year = models.ForeignKey(Year,on_delete=models.CASCADE,related_name="Subjects",default=None,null=True)
    Lectures = models.Manager["Lecture"]
#------------------

class Lecture(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    Subject = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="Lectures")
    User =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Lectures",null=True,default=None)
    Questions = models.Manager["Question"]
#------------------

class Question(models.Model):
    ID = models.AutoField(primary_key=True)
    class QType(models.IntegerChoices):
        CHOOSE = 0, "Choose"
        WRITTEN = 1, "Written"
        COMPLEX = 2, "Complex"
    class QEase(models.IntegerChoices):
        Easy = 0, "Easy"
        Medium = 1, "Medium"
        Hard = 2, "Hard"
    Text_Url = models.CharField(max_length=400)
    Type = models.IntegerField(choices=QType.choices, default=QType.CHOOSE)
    Ans = models.CharField(max_length=400)
    lecture = models.ForeignKey(Lecture,on_delete=models.CASCADE,related_name="Questions")
    IsInAnExam = models.BooleanField()
    Ease = models.IntegerField(choices=QEase.choices,default=QEase.Easy)
    soln = models.Manager["soln"]
    User =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Questions",null=True,default=None)
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
    Settings = models.ManyToManyField(Setting, through='ExamSetting')
    User =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Exams",null=True,default=None)
    classRooms:models.Manager["classRoom"]
    solns = models.Manager["soln"]
#------------------
class ExamSetting(models.Model):
    ID = models.AutoField(primary_key=True)
    Exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    Setting = models.ForeignKey(Setting, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('Setting',) 
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