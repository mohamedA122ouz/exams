from typing import Any, Optional, cast

from core.services.types.userType import IUserHelper


class TermService:
    def showTerms(self,user,year_id:Optional[str|int],limit:int=100,last_id:int=0)->list[dict[str,Any]]|dict[str,str]:
        user = cast(IUserHelper,user)
        if not year_id:
            return {"year_id":"cannot be null"}
        terms = user.Terms.filter(Year__ID=year_id,ID__gt=last_id)[:limit].values()
        return list(terms)
    #------------------
    def createTerm(self,user,name:Optional[str],year_id:Optional[int|str]):
        if not (name):
            return {"name":"term name cannot be null"}
        if not year_id:
            return {"year_id":"year ID cannot be null"}
        user = cast(IUserHelper,user)
        year = user.Years.filter(ID=year_id).first()
        if not year:
            return {"year":"year doesn't exist"}
        term = user.Terms.create(Year=year,Name=name)
        if term:
            return {"success":"Term Created Successfully"}
        return {"fail":"term creation faild"}
    #------------------
#------------------CLASS_ENDED#------------------