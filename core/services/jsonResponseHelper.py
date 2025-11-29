from typing import Any

from django.http import JsonResponse


def ResponseHelper(res:dict[str,str]|list[dict[str,Any]])->JsonResponse:
    if isinstance(res,list):
        return JsonResponse(res,safe=False)
    if hasattr(res,"fail"):
        return JsonResponse(res,status=500)
    elif hasattr(res,"success"):
        return JsonResponse(res)
    else:
        return JsonResponse(res,status=400)
#------------------