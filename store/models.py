from django.db import models
from django.contrib.auth.models import User
from typing import TYPE_CHECKING
from django.db.models.fields.related_descriptors import ManyRelatedManager
from core.models.Exams_models import AttachmentLicence, paymentLocker
from store.utils.types.RequestStatus import RequestStatus

class Store(models.Model):
    StoreOwner = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name="StoreOwner")
    Name = models.CharField(max_length=50,null=False)
    ID = models.AutoField(primary_key=True)
    Tag = models.CharField(max_length=50,null=False,unique=True)
#---------------
class StoreItems(models.Model):
    Name = models.CharField(max_length=50,null=False)
    ID = models.AutoField(primary_key=True)
    Serial = models.CharField(null=False,unique=True)
    Stars = models.FloatField(null=False,default=0) # 0 - 5 stars
    Price = models.DecimalField(null=False,default=0,decimal_places=3,max_digits=10)
    Amount = models.IntegerField(null=False,default=0)
    ReviewsCount = models.IntegerField(null=False,default=0)
    attachments =models.ForeignKey("StoreAttachments",on_delete=models.CASCADE,null=False,related_name="StoreItems")
    if TYPE_CHECKING:
        Catigories: ManyRelatedManager["Catigories"]
#---------------
class StoreAttachments(models.Model):
    # ATTACHMENT FIELDS
    ID = models.AutoField(primary_key=True)
    name = models.TextField(null=False,blank=False,default='NO_NAME')
    Attachments = models.FileField(upload_to="uploads/store/",null=True,default=None)
    attachmentLicence = models.OneToOneField(AttachmentLicence,on_delete=models.CASCADE,related_name='classRoomAttachment')
    if TYPE_CHECKING:
        StoreItems:models.Manager[StoreItems]
#---------------
class Catigories(models.Model):
    Name = models.CharField(max_length=50,null=False)
    ID = models.AutoField(primary_key=True)
    StoreItems = models.ManyToManyField(StoreItems,related_name="Catigories")
#---------------
class Reviews(models.Model):
    ID = models.AutoField(primary_key=True)
    Reviewer = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name="Reviewer")
    Text = models.TextField(null=True)
    Stars = models.FloatField(null=False,default=0) # 0 - 5 stars
#---------------
class Requests(models.Model):
    ID = models.AutoField(primary_key=True)
    RequestOwner = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name="OwnedRequest")
    Amount = models.SmallIntegerField(default=1,null=False)
    PaidAmount = models.DecimalField(null=False,default=0,decimal_places=3,max_digits=10)
    RemainingAmount = models.DecimalField(null=False,default=0,decimal_places=3,max_digits=10)
    UpdateTime = models.DateTimeField(auto_now=True)
    Status = models.IntegerField(choices=RequestStatus.choices())
    Installment = models.BooleanField(default=False)
    Last_Transcation = models.BooleanField(default=False)
    if TYPE_CHECKING:
        payments:models.Manager["storePayment"]
#---------------
class storePayment(models.Model):
    PaidRequest = models.ForeignKey(Requests,related_name="Payments",on_delete=models.CASCADE,null=False)
    PaidUser = models.ForeignKey(User,related_name="paidUser-",on_delete=models.CASCADE,null=False)
    Amount = models.DecimalField(null=False,default=0,decimal_places=3,max_digits=10)
    TransactionType = models.IntegerField(choices=RequestStatus.choices())
    locker = models.ForeignKey(paymentLocker,related_name="storePayment",on_delete=models.CASCADE,null=False)
#---------------