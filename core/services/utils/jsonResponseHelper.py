from typing import Any, cast

from django.forms import model_to_dict
from django.http import JsonResponse
from django.db.models import Model
from core.services.types.questionType import GeneralOutput

def ResponseHelper(res:dict[str,str]|list[dict[str,Any]]|dict[str,Any] | Model | list[Model] | GeneralOutput |None)->JsonResponse:
    if isinstance(res,list) and len(res) == 0:
        return JsonResponse({"empty":"no entries"},status=201)
    if not res:
        return JsonResponse({"null":"server return null"},status=500)
    if isinstance(res,Model):
        return JsonResponse(model_to_dict(res))
    #---------------
    if "error" in res and "isSuccess" in res and "output" in res:
        _pOutput = cast(GeneralOutput,res)
        if _pOutput["error"] is None:
            if isinstance(_pOutput['output'],list):
                return ResponseHelper(_pOutput["output"])
            return JsonResponse(_pOutput["output"])
        if _pOutput["output"] is None:
            return ResponseHelper(_pOutput["error"])
        #---------------
    #---------------
    if isinstance(res,list):
        if len(res) == 0:
            return JsonResponse({"list":[]})
        else:
            item = res[0]
            if isinstance(item,Model):
                return JsonResponse({"list":[ model_to_dict(cast(Model,i)) for i in res]})
            #---------------
            else:
                return JsonResponse({"list":res})
            #---------------
        #---------------
    #---------------
    if hasattr(res,"fail") or "fail" in res or "failed" in res or hasattr(res,"failed"):
        return JsonResponse(res,status=500)
    elif hasattr(res,"success") or "success" in res:
        if isinstance(res,Model):
            return JsonResponse(model_to_dict(res))
        return JsonResponse(res)
    else:
        for key in res:
            if 'not found' in res[key]: #type:ignore
                return JsonResponse(res,status=404)
            if 'unauthorized' == key: #type:ignore
                return JsonResponse(res,status=403)
        return JsonResponse(res,status=400)
#---------------