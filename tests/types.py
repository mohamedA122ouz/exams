from pydantic import BaseModel

class User_type(BaseModel):
    username:str
    password:str
    email:str
#---------------
