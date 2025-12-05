from typing import Any

from django.http import JsonResponse


def ResponseHelper(res:dict[str,str]|list[dict[str,Any]])->JsonResponse:
    if isinstance(res,list):
        return JsonResponse(res,safe=False)
    if hasattr(res,"fail") or "fail" in res:
        return JsonResponse(res,status=500)
    elif hasattr(res,"success") or "success" in res:
        return JsonResponse(res)
    else:
        return JsonResponse(res,status=400)
#------------------