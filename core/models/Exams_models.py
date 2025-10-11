from django.db import models
from django.contrib.auth.models import User




class Year(models.Model):
    Name = models.CharField(max_length=50)
    User = models.ForeignKey(User,on_delete=models.CASCADE,related_name="Years")
    
    Terms = models.Manager["Term"]

class Term(models.Model):
    Name = models.CharField(max_length=50)
    Year = models.ForeignKey(Year,on_delete=models.CASCADE,related_name="Terms")
    
    Subjects = models.Manager["Subject"]

class Subject(models.Model):
    Name = models.CharField(max_length=50)
    Term = models.ForeignKey(Term,on_delete=models.CASCADE,related_name="Subjects")
    
    Lectures = models.Manager["Lecture"]

class Lecture(models.Model):
    Name = models.CharField(max_length=50)
    Subject = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="Lectures")
    
    Questions = models.Manager["Question"]

class Question(models.Model):
    class QType(models.IntegerChoices):
        CHOOSE = 0, "Choose"
        WRITTEN = 1, "Written"
        COMPLEX = 2, "Complex"
    Text_Url = models.CharField(max_length=400)
    Type = models.IntegerField(choices=QType.choices, default=QType.CHOOSE)
    Ans = models.CharField(max_length=400)
    lecture = models.ForeignKey(Lecture,on_delete=models.CASCADE,related_name="Questions")
    IsInAnExam = models.BooleanField()
    soln = models.Manager["soln"]

class Setting(models.Model):
    ExamInterval = models.TimeField()
    AutoCorrect = models.BooleanField(default=True)
    QuestionByQuestion = models.BooleanField(default=True)
    TrackSolutions = models.BooleanField(default=True)
    Public = models.BooleanField(default=False)
    AllowDownLoad = models.BooleanField(default=False)

class Exam(models.Model):
    IsScheduled = models.BooleanField()
    Subject = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="Exams")
    Settings = models.ManyToManyField(Setting, through='ExamSetting')
    
    solns = models.Manager["soln"]

class ExamSetting(models.Model):
    Exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    Setting = models.ForeignKey(Setting, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('Setting',) 


class soln(models.Model):
    Exam = models.ForeignKey(Exam,on_delete=models.CASCADE,related_name="Solns")
    Question = models.ForeignKey(Question,on_delete=models.CASCADE,related_name="Solns")
    User = models.ForeignKey(User,on_delete=models.CASCADE,related_name="Solns")
