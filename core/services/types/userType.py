from typing import TYPE_CHECKING, Optional, Protocol
from django.db.models import Manager

from core.models.Exams_models import chatRoom
if TYPE_CHECKING:
    from core.models.Exams_models import AttachmentLicence, Committe, CommitteAllowedList, PrivilegeMapper, WatchHistory, balance, classRoom,Exam_BlackList, solutionsSheet,Privileges,Payment_ChatRoom,Payment_Attachment,Payment_classRoom,Messages,Year, Term, Subject, Lecture, Exam, Question, Soln,ProfileSettings
    from django.db.models.fields.related_descriptors import ManyRelatedManager

class IUserHelper(Protocol):
    Years: Manager["Year"]
    Terms: Manager["Term"]
    Subjects: Manager["Subject"]
    Lectures: Manager["Lecture"]
    Exams: Manager["Exam"]
    Questions: Manager["Question"]
    Solns: Manager["Soln"]
    Owned_classRooms:Manager["classRoom"]
    Settings:Optional["ProfileSettings"]
    solnSheet:Manager["solutionsSheet"]
    Balance:Optional["balance"]
    Owned_chatRoom:Manager["chatRoom"]
    Owned_classroomattachments:Manager["Payment_classRoom"]
    if TYPE_CHECKING:
        blackListed:ManyRelatedManager["Exam"]
        ExamBlackListTable:ManyRelatedManager["Exam_BlackList"]
        Privileges:ManyRelatedManager["Privileges"]
        Payment_ChatRoom:Manager["Payment_ChatRoom"]
        Payment_Attachment:Manager["Payment_Attachment"]
        Payment_classRoom:Manager["Payment_classRoom"]
        youCorrected:Manager[Soln]
        attachmentLicence:Manager[AttachmentLicence]
        inspector:Manager['Committe']
        allowedIn:Manager['CommitteAllowedList']
        attachmentHistory:Manager['WatchHistory']
        PrivilegeMapper:Manager["PrivilegeMapper"]
        Messages:Manager["Messages"]
        SeenMessages:ManyRelatedManager["Messages"]
        chatRooms:ManyRelatedManager["chatRoom"]
    #------------------
#---------------
