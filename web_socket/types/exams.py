from typing import Any, Literal, Optional, TypedDict


class MessageEvent(TypedDict):
    RequestType:Literal["Committee","ChatRoom"]
    TriggerPoint:str
    Params:dict[str,Any]
    Description:Optional[str]
#------------------