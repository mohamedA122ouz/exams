from typing import Literal, TypedDict

class AnsParserOutput(TypedDict):
    answers:str
    questions:str
    questionType:Literal[0,1,2]
#------------------
class ExamSetting(TypedDict):
    subjectName:str
    yearName:str
    termName:str
    lectureName:str
    randomization:bool
#------------------
class QuestionEase(TypedDict):
    ease:Literal[0,1,2]
    count:int
#------------------
class ExamAutoGenerator(TypedDict):
    generatorSettings:ExamSetting
    questions:list[QuestionEase]
#------------------