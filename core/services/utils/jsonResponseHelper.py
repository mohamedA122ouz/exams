from typing import Any, cast

from django.forms import model_to_dict
from django.http import JsonResponse
from django.db.models import Model
from core.services.types.questionType import parserOutput


def ResponseHelper(res:dict[str,str]|list[dict[str,Any]]|dict[str,Any])->JsonResponse:
    if "error" in res and "isSuccess" in res and "output" in res:
        _pOutput = cast(parserOutput,res)
        if not _pOutput["isSuccess"] and _pOutput["error"]:
            return JsonResponse(_pOutput["error"],status=400)
        #------------------
    #------------------
    if isinstance(res,list):
        return JsonResponse(res)
    if hasattr(res,"fail") or "fail" in res:
        return JsonResponse(res,status=500)
    elif hasattr(res,"success") or "success" in res:
        if isinstance(res,Model):
            return JsonResponse(model_to_dict(res))
        return JsonResponse(res)
    else:
        return JsonResponse(res,status=400)
#------------------