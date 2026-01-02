

from typing import Optional, TypeVar
from core.services.types.questionType import GeneralOutput

T = TypeVar('T')
def GOutput(output:Optional[T]=None,error:Optional[dict[str,str]]=None,issuccess=False)->GeneralOutput[Optional[T]]:
    if not issuccess:
        issuccess = False
        if output:
            issuccess = True
        #------------------
        elif not error:
            issuccess = True
    #------------------
    return {
        'error':error,
        'isSuccess':issuccess,
        'output':output
    }
#------------------