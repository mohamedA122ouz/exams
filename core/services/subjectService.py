import json
from typing import Any, Optional, cast

from core.services.utils.userHelper import IUserHelper


class SubjectService:
    def showSubjects(self,user)->dict[str,str]|list[dict[str,Any]]: 
        user = cast(IUserHelper,user)
        if not user:
            return {"subjects":"required login"}
        subjects = user.Subjects.values()
        return list(subjects)
    #------------------
    def createSubject(self,user,year_id:Optional[int|str],term_id:Optional[str|int],name:Optional[str]):
        user = cast(IUserHelper,user)
        if not term_id:
            return {"term_id":"term Id cannot be null"}
        if not year_id:
            return {"year_id":"cannot year ID be null"}
        if not name:
            return {"name":"cannot give null name"}
        term = user.Terms.filter(ID=term_id).first()
        if not term:
            return {"creation":"faild term is not exist"}
        year = user.Years.filter(ID=year_id).first()
        if not year:
            return {"creation":"faild year is not exist"}
        subject = user.Subjects.create(
            Name=name,
            Year=year,
            Term=term
        )
        if not subject:
            return {"fail":"faild no reason specified"}
        return {"success":"subject created"}
    #------------------
#------------------CLASS_ENDED#------------------