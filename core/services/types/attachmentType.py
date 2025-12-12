from typing import Literal, TypedDict

class Attachments(TypedDict):
    type:Literal["img","audio","video","youtube"]
    link:str
#------------------