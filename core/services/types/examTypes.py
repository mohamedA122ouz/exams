from datetime import datetime
from typing import Optional, TypedDict
from core.services.types.questionType import ShareWithEnum


class Location(TypedDict):
    Xaxis:float
    Yaxis:float
#------------------
class ExamSettings(TypedDict):
    Locations:Optional[Location]
    PreventOtherTabs:bool
    Duration_min:int
    AutoCorrect:bool
    QuestionByQuestion:bool
    ShareWith:ShareWithEnum
    AllowDownload:bool
    StartAt:Optional[datetime]
    EndAt:Optional[datetime]
#------------------
class examRequest(TypedDict):
    title:str
    question_ids:list[int]
    subject_id:int
    settings:Optional[ExamSettings]
#------------------