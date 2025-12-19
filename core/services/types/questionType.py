from typing import Any, Generic, Literal, Optional, Protocol, TypeVar, TypedDict
from enum import IntEnum

from core.services.types.attachmentType import Attachments

class QuestionType(IntEnum):
    MCQ_ONE_ANS = 0
    MCQ_MORE_ANS = 1
    WRITTEN_QUETION = 2
    COMPLEX = 3
    @classmethod
    def choices(cls) -> list[tuple[int, str]]:
        return [(e.value, e.name) for e in cls]
#------------------
class QuestionEase(IntEnum):
    EASY = 0
    MEDIUM = 1
    HARD = 2
    @classmethod
    def choices(cls) -> list[tuple[int, str]]:
        return [(e.value, e.name) for e in cls]
#------------------
class ShareWithEnum(IntEnum):
    CLASSROOM = 0
    ANY_ONE_WITH_LINK = 1
    PRIVATE = 2
    @classmethod
    def choices(cls) -> list[tuple[int, str]]:
        return [(e.value, e.name) for e in cls]
#------------------
class QuestionFromFront(TypedDict):
    """Question Came from frontend and need to convert for database insertion or quesiton need to be sent to frontend"""
    answers:str
    question:str # Exam with $ATTACHMENT_INDEX
    questionType:int|QuestionType
    ease:int
    choices:Optional[list[str]]
    attachments:Optional[list[Attachments]]
    lecture_id:int
#------------------
class AutoGenExamSetting(TypedDict):
    subjectID:str
    yearID:str
    termID:str
    randomization:bool
#------------------
class QuestionSelector(TypedDict):
    lectureID:int
    ease:int|QuestionEase
    count:int
#------------------
class ExamAutoGenerator(TypedDict):
    generatorSettings:AutoGenExamSetting
    questions:list[QuestionSelector]
#------------------
class QuestionToInsert(TypedDict):
    """question here is ready to be inserted to database or alread come from database"""
    question:str # Exam within Exam language
    ans:str
    type:int|QuestionType
    ease:int|QuestionEase
    lecture_id:int
#------------------
T = TypeVar("T")
class parserOutput(TypedDict,Generic[T]):#parser output stamp
    isSuccess:bool
    output:T
    error:Optional[dict[str,str]]
#------------------