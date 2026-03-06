from typing import Any, Literal, TypedDict

class Attachments(TypedDict):
    type:Literal["img","audio","video","youtube"]
    link:str
#---------------

class AttachDependOn(TypedDict):
    dependOnTable:str
    conditionsOnFields:Any
#---------------