from typing import Literal, TypedDict

class AnsParserOutput(TypedDict):
    answers:str
    questions:str
    questionType:Literal[0,1,2]
#------------------