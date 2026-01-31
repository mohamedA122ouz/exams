from datetime import datetime
from random import choice
from typing import TYPE_CHECKING, Optional
from django.db import models
from django.contrib.auth.models import User
from core.services.types.submitReason import SubmitReason
from core.services.types.questionType import QuestionEase, QuestionType, ShareWithEnum
from core.services.types.transactionType import TransactionType
from django.db.models import Manager
if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import ManyRelatedManager,ForwardOneToOneDescriptor



class ProfileSettings(models.Model):
    ID = models.AutoField(primary_key=True)
    PreferedLang = models.ForeignKey("supportedLanguages",on_delete=models.CASCADE,null=False,related_name="Profiles")
    User = models.OneToOneField(User,on_delete=models.CASCADE,related_name="Settings")
    socketID = models.TextField(null=True,default=None)
    Warnings = models.SmallIntegerField(default=3)
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
    Year:models.ForeignKey["Year"] = models.ForeignKey(Year,on_delete=models.CASCADE,related_name="Subjects",default=None,null=True)
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
    OwnedBy = models.ForeignKey(User,on_delete=models.CASCADE,related_name="Questions",null=True,default=None)
    if TYPE_CHECKING:
        Exams:ManyRelatedManager["Exam"] # only owner should see this else shouldn't see
        Solns:Manager["Soln"]
        ExamQuestionsTable:Manager["Exam_Questions"]
#------------------
class Exam(models.Model):
    ID = models.AutoField(primary_key=True)
    TotalMark = models.FloatField(null=False,default=0)
    PassKey = models.TextField(null=True,blank=True)
    Title = models.TextField(null=True,blank=True)
    CreatedAt = models.DateTimeField(null=False,default=datetime.now())
    Subject:models.ForeignKey["Subject"] = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="Exams")
    Owner =  models.ForeignKey(User,on_delete=models.CASCADE,related_name="Exams",null=True,default=None)
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
    blackListedStudents = models.ManyToManyField(User,through="Exam_BlackList",related_name="blackListed")
    Questions = models.ManyToManyField("Question", through="Exam_Questions")
    if TYPE_CHECKING:
        ExamBlackListTable :ManyRelatedManager["Exam_BlackList"]
        ClassRooms:ManyRelatedManager["classRoom"]
        SolutionSheets:Manager["solutionsSheet"]
#------------------
class Exam_BlackList(models.Model):
    student = models.ForeignKey(User,models.CASCADE,related_name="ExamBlackListTable")
    exams = models.ForeignKey(Exam,models.CASCADE,related_name="ExamBlackListTable")
    Reason = models.TextField(null=True,blank=True)
#------------------
class Exam_Questions(models.Model):
    Exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    Question = models.ForeignKey(Question, on_delete=models.CASCADE)
    Order = models.IntegerField(default=0)
    degree = models.FloatField(default=0)
    sectionName = models.CharField(max_length=150,null=True,blank=True)
#------------------
class Location(models.Model):
    ID = models.AutoField(primary_key=True)
    Xaxis = models.FloatField()
    Yaxis = models.FloatField()
    buildingArea = models.FloatField(null=False)
    Exam = models.ForeignKey(Exam,on_delete=models.CASCADE,related_name="Locations")
#------------------
class Soln(models.Model):
    ID = models.AutoField(primary_key=True)
    SolvedBy = models.ForeignKey(User,on_delete=models.CASCADE,related_name="Solns")
    Content = models.TextField(null=False,blank=True)
    Note = models.TextField(null=False,blank=True)
    Degree = models.FloatField(default=0.0)
    SolutionSheet = models.ForeignKey("solutionsSheet",on_delete=models.CASCADE,related_name="solutions")
    Question:models.ForeignKey["Question"] = models.ForeignKey("Question",on_delete=models.CASCADE,related_name="Solns")
    correctedBy = models.ForeignKey(User,on_delete=models.CASCADE,related_name="youCorrected",null=True,blank=True)
#------------------
class classRoom(models.Model):
    #PAYMENT SETTINGS
    paymentAmount = models.DecimalField(null=False,default=0,decimal_places=3,max_digits=10)
    PaymentExpireInterval_MIN = models.IntegerField(null=False,default=0)
    PaymentAccessMaxCount = models.IntegerField(null=False,default=0)
    # CLASSROOM FIELDS
    ID = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=50,null=True,default="")
    OwnedBy = models.OneToOneField(User,on_delete=models.CASCADE,related_name="OwnedClasses",null=False)
    HideFromSearch = models.BooleanField(default=False,null=False)
    Exams = models.ManyToManyField(Exam,through="classRoom_Exam",related_name="ClassRooms")
    if TYPE_CHECKING:
        Privileges: models.ForeignKey["Privileges"]
        Payment_classRoom:Manager["Payment_classRoom"]
        chatRooms:Manager["chatRoom"]
        Attachments: ManyRelatedManager["ClassRoomAttachment"]
        cl_clAttach:Manager['classRoom_ClassRoomAttachment']
#------------------
class ClassRoomAttachment(models.Model):
    #PAYMENT SETTINGS
    paymentAmount = models.DecimalField(null=False,default=0,decimal_places=3,max_digits=10)
    PaymentExpireInterval_MIN = models.IntegerField(null=False,default=0)
    PaymentAccessMaxCount = models.IntegerField(null=False,default=0)
    # ATTACHMENT FIELDS
    ID = models.AutoField(primary_key=True)
    Attachments = models.FileField(upload_to="uploads/",null=True,default=None)
    classRoom = models.ManyToManyField(classRoom,related_name="Attachments",through='classRoom_ClassRoomAttachment')
    attachmentLicence = models.OneToOneField("AttachmentLicence",on_delete=models.CASCADE,related_name='classRoomAttachment')
    if TYPE_CHECKING:
        Payment_Attachment:Manager["Payment_Attachment"]
        cl_clAttach:Manager['classRoom_ClassRoomAttachment']
#------------------
class classRoom_ClassRoomAttachment(models.Model):
    classRoom = models.ForeignKey("classRoom",models.CASCADE,"cl_clAttach")
    order = models.IntegerField()
    isOrderDepenent = models.BooleanField(default=False)
    ClassRoomAttachment = models.ForeignKey("ClassRoomAttachment",models.CASCADE,"cl_clAttach")
#------------------
class Payment_classRoom(models.Model):
    TransactionTime = models.DateTimeField(auto_now=True)
    ExpireDateTime = models.DateTimeField(null=True,blank=True)
    AccessCounter = models.BigIntegerField(null=True,blank=True)
    Owner = models.ForeignKey(User,on_delete=models.CASCADE,null=False)
    locker = models.ForeignKey("paymentLocker",null=False,on_delete=models.CASCADE,related_name="Payment_classRoom")
    classRoom:models.ForeignKey["classRoom"] = models.ForeignKey("classRoom",null=False,on_delete=models.CASCADE,related_name="Payment_classRoom")
#------------------

class Payment_Attachment(models.Model):
    ExpireDateTime = models.DateTimeField(null=True,blank=True)
    AccessCounter = models.BigIntegerField(null=True,blank=True)
    Owner = models.ForeignKey(User,on_delete=models.CASCADE,null=False)
    locker = models.ForeignKey("paymentLocker",null=False,on_delete=models.CASCADE,related_name="Payment_Attachment")
    classRoomAttachment = models.ForeignKey("ClassRoomAttachment",null=False,on_delete=models.CASCADE,related_name="Payment_Attachment")
    TransactionTime = models.DateTimeField(auto_now=True)
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
    #this is a bug cause soln sheet must be one include all soln and question so the many to many with exam and and soln must have other class
    LastUpdate = models.DateTimeField(null=False,default=datetime.now())
    SubmitReason = models.IntegerField(choices= SubmitReason.choices())
    SpecifiedTextReason = models.TextField(blank=True,null=False)
    IsSubmitted = models.BooleanField(default=False,null=False)
    TotalMark = models.FloatField(null=False, default=0)
    Student = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name="solnSheet")
    Exam = models.ForeignKey("Exam",on_delete=models.CASCADE,related_name="SolutionSheets")
    if TYPE_CHECKING:
        Solns:Manager["Soln"]
#------------------
class Privileges(models.Model):
    # Privileges
    Name = models.CharField(null=False,max_length=50)
    # RELATIONS
    ClassRooms:models.ForeignKey["classRoom"] = models.ForeignKey("classRoom",on_delete=models.CASCADE,related_name="Privileges",null=True)
    User = models.ManyToManyField(User,related_name="Privileges",default=1)
    Privilege = models.IntegerField(null=False,blank=False,default=0)
#------------------
class chatRoom(models.Model):
    # PAYMENT SETTINGS
    paymentAmount = models.DecimalField(null=False,default=0,decimal_places=3,max_digits=10)
    PaymentExpireInterval_MIN = models.IntegerField(null=False,default=0)
    PaymentAccessMaxCount = models.IntegerField(null=False,default=0)
    # CHATROOM FIELDS
    Name = models.CharField(max_length=50,null=False)
    classRoom = models.ForeignKey("classRoom",null=False,on_delete=models.CASCADE,related_name="chatRooms")
    if TYPE_CHECKING:
        # Privileges:ManyRelatedManager["Privileges"]
        Messages:Manager["messages"]
        Payment_ChatRoom:Manager["Payment_ChatRoom"]
#------------------
class Payment_ChatRoom(models.Model):
    TransactionTime = models.DateTimeField(auto_now=True)
    ExpireDateTime = models.DateTimeField(null=True,blank=True)
    AccessCounter = models.BigIntegerField(null=True,blank=True)
    Owner = models.ForeignKey(User,on_delete=models.CASCADE,null=False)
    locker = models.ForeignKey("paymentLocker",null=False,on_delete=models.CASCADE,related_name="Payment_ChatRoom")
    chatRoom = models.ForeignKey("chatRoom",null=False,on_delete=models.CASCADE,related_name="Payment_ChatRoom")
#------------------
class messages(models.Model):
    Owner = models.ForeignKey(User,on_delete=models.CASCADE,null=False)
    text = models.TextField(null=False)
    classRoom = models.ForeignKey("classRoom",on_delete=models.CASCADE)
#------------------
class paymentLocker(models.Model):
    totalAmount = models.DecimalField(null=False,default=0,decimal_places=3,max_digits=10)
    lastUpdate = models.DateTimeField(null=False)
    count = models.BigIntegerField(null=False,default=0)
    if TYPE_CHECKING:
        Payment_ChatRoom:Manager["Payment_ChatRoom"]
        Payment_Attachment:Manager["Payment_Attachment"]
        Payment_classRoom:Manager["Payment_classRoom"]
#------------------
class AttachmentLicence(models.Model):
    ID  = models.AutoField(primary_key=True)
    owner = models.OneToOneField(User,on_delete=models.CASCADE,related_name='attachmentLicence')
    uploadTime = models.DateTimeField(auto_now=True)
    FileFingerPrint = models.TextField()
    RequireSecurity = models.BooleanField(default=False)
    if TYPE_CHECKING:
        classRoomAttachment:ClassRoomAttachment
#------------------
class dependenciesRepo: 
    # This table must not connect with other tables
    # This table is just a placeholder for the dependencies
    # how this works this is like a small logic 
    dependentTable = models.TextField() # main table like Attachment
    dependOnTable = models.TextField() # main table depend on this table like exams
    value = models.TextField() # value
#------------------

#-----------------------------------------------
#-----------------------------------------------
#-----------------------------------------------
#-----------------------------------------------
#-----------------------------------------------
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


