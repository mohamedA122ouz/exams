

from typing import Optional, TypeVar, cast

from rest_framework.serializers import Serializer
from core.services.types.questionType import GeneralOutput

T = TypeVar('T')
def GOutput(output:Optional[T|Serializer]=None,error:Optional[dict[str,str]]=None,issuccess=False)->GeneralOutput[Optional[T]]:
    if isinstance(output,Serializer):
        if not output.is_valid():
            newOutput ={}
            
            for key in  output.errors:
                if key in output.data and output.data[key] is not None:
                    if 'not_exist' in output.errors[key][0].code:
                        newOutput[key] = 'not found'
                    #---------------
                    else:
                        newOutput[key] = 'value error'
                    #---------------
                else:
                    newOutput[key] = 'cannot be null'
                #---------------
            #---------------
            return {
                'error':newOutput,
                'isSuccess':False,
                'output':None
            }
        else:
            return {
                'output':output.validated_data,
                'isSuccess':True,
                'error':None
            }
        #---------------
    #---------------
    if not issuccess:
        issuccess = False
        if output:
            issuccess = True
        #---------------
        elif not error:
            issuccess = True
    #---------------
    return {
        'error':error,
        'isSuccess':issuccess,
        'output':output
    }
#---------------