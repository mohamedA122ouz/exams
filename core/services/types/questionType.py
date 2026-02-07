from typing import Any, Generic, Literal, Optional, Protocol, TypeVar, TypedDict
from enum import IntEnum

from core.services.types.attachmentType import Attachments


class ScoringMode(IntEnum):
    DEFAULT = 0
    MULTI_ANS_ONE_ENOUGH = 1
    MULTI_ANS_PARTITION = 2
    @classmethod
    def choices(cls):
        return [(k.value,k.name) for k in cls]
#------------------
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
    CLASSROOM_DEFAULT = 0
    ANY_ONE_WITH_LINK = 1
    PRIVATE = 2
    CLASSROOM_PUBLIC = 3
    
    @classmethod
    def choices(cls) -> list[tuple[int, str]]:
        return [(e.value, e.name) for e in cls]
#------------------
class QuestionFromFront(TypedDict):
    """Question Came from frontend and need to convert for database insertion or quesiton need to be sent to frontend"""
    ID:Optional[int]
    answers:str
    question:str # question with $ATTACHMENT_INDEX
    questionType:int|QuestionType
    ease:int
    choices:Optional[list[str]]
    attachments:Optional[list[Attachments]]
    lecture_id:int
    sectionName:Optional[str]
    degree:Optional[float]
#------------------
class QuestionToFront(TypedDict):
    """Question Came from frontend and need to convert for database insertion or quesiton need to be sent to frontend"""
    answers:Optional[str]
    question:str # question with $ATTACHMENT_INDEX
    questionType:int|QuestionType
    ease:int
    choices:Optional[list[str]]
    attachments:Optional[list[Attachments]]
    lecture_id:int
    sectionName:Optional[str]
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
class GeneralOutput(TypedDict,Generic[T]):#parser output stamp
    """
    validator parser and much more any Output need to know if success and if successed need to pass data or pass error on fail
    
    :var isSuccess: Description
    :vartype isSuccess: bool
    :var output: Description
    :vartype output: T
    :var error: Description
    
    """
    isSuccess:bool
    output:T
    error:Optional[dict[str,str]]
#------------------