from typing import Any, Optional, cast
from core.services.utils.userHelper import IUserHelper


class LectureService:
    def showLectures(self,user,subject_id:Optional[int|str],limit:int=100,last_id:int=0)->dict[str,str]|list[dict[str,Any]]:
        user = cast(IUserHelper,user)
        if not subject_id:
            return {"subject_id":"ID cannot be null"}
        lecture = user.Lectures.filter(Subject__ID=subject_id,ID__gt=last_id)[:limit].values()
        if not lecture:
            return {"lecture":"no lecture found"}
        return list(lecture)
    #------------------
    def createLectures(self,user,name:Optional[str],subject_id:Optional[int|str])->dict[str,str]:
        user = cast(IUserHelper,user)
        if not name:
            return {"name":"cannot give null name"}
        if not subject_id:
            return {"subject_id":"cannot be null"}
        subject = user.Subjects.filter(ID=subject_id).first()
        if not subject:
            return {"subject":"is not found"}
        if user.Lectures.filter(Name=name).exists():
            return {"name":"cannot create two lectures with the same name"}
        lecture = user.Lectures.create(
            Name=name,
            Subject=subject
        )
        if not lecture:
            return {"fail":"no lecture created"}
        return {"success":"successful"}
    #------------------
#------------------CLASS_ENDED#------------------