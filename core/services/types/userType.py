from typing import TYPE_CHECKING, Optional, Protocol
from django.db.models import Manager
from core.models import Year, Term, Subject, Lecture, Exam, Question, Soln,ProfileSettings
from core.models.Exams_models import classRoom,ExamBlackList
if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import ManyRelatedManager

class IUserHelper(Protocol):
    Years: Manager[Year]
    Terms: Manager[Term]
    Subjects: Manager[Subject]
    Lectures: Manager[Lecture]
    Exams: Manager[Exam]
    Questions: Manager[Question]
    Solns: Manager[Soln]
    OwnedClasses:Manager[classRoom]
    Teaches:Manager[classRoom]
    StudyAt:Manager[classRoom]
    Administrate:Manager[classRoom]
    Settings:Optional[ProfileSettings]
    if TYPE_CHECKING:
        blackListed:ManyRelatedManager[Exam]
        ExamBlackListTable :ManyRelatedManager["ExamBlackList"]
#------------------
