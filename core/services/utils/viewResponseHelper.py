from typing import Any, Mapping


def HTMLResponse(res:dict[str,str]|list[dict[str,Any]])->Mapping[str,Any]:
    if isinstance(res,list):
        return {"list":res}
    return res