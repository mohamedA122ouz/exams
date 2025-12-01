from typing import TypedDict

class AnsParserOutput(TypedDict):
    answers:list[int]
    questions:list[str]
#------------------