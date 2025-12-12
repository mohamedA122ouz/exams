# mypy_stubs/django/contrib/auth/models.pyi
from typing import Protocol
from django.db.models import Manager
from core.models import Year, Term, Subject, Lecture, Exam, Question, soln
from core.models.Exams_models import classRoom

class IUserHelper(Protocol):
    Years: Manager[Year]
    Terms: Manager[Term]
    Subjects: Manager[Subject]
    Lectures: Manager[Lecture]
    Exams: Manager[Exam]
    Questions: Manager[Question]
    Solns: Manager[soln]
    classRoomsOwner:Manager[classRoom]
    classRoomsMember:Manager[classRoom]
    Admin:Manager[classRoom]
#------------------
