from typing import Any, cast

from django.forms import model_to_dict
from django.http import JsonResponse
from django.db.models import Model
from core.services.types.questionType import parserOutput

def ResponseHelper(res:dict[str,str]|list[dict[str,Any]]|dict[str,Any] | Model | list[Model])->JsonResponse:
    if isinstance(res,Model):
        return JsonResponse(model_to_dict(res))
    #------------------
    if "error" in res and "isSuccess" in res and "output" in res:
        _pOutput = cast(parserOutput,res)
        if not _pOutput["isSuccess"] and _pOutput["error"]:
            return JsonResponse(_pOutput["error"],status=400)
        #------------------
    #------------------
    if isinstance(res,list):
        if len(res) == 0:
            return JsonResponse({"list":[]})
        else:
            item = res[0]
            if isinstance(item,Model):
                return JsonResponse({"list":[ model_to_dict(cast(Model,i)) for i in res]})
            #------------------
            else:
                return JsonResponse({"list":res})
            #------------------
        #------------------
    #------------------
    if hasattr(res,"fail") or "fail" in res:
        return JsonResponse(res,status=500)
    elif hasattr(res,"success") or "success" in res:
        if isinstance(res,Model):
            return JsonResponse(model_to_dict(res))
        return JsonResponse(res)
    else:
        return JsonResponse(res,status=400)
#------------------