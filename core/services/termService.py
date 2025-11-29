from typing import Any, Optional, cast

from core.services.userHelper import IUserHelper


class TermService:
    def showTerms(self,user,year_id:Optional[str|int])->list[dict[str,Any]]|dict[str,str]:
        user = cast(IUserHelper,user)
        if not year_id:
            return {"year_id":"cannot be null"}
        terms = user.Terms.filter(Year__ID=year_id).values()
        return list(terms)
    #------------------
    def createTerm(self,user,name:Optional[str],year_id:Optional[int|str]):
        if not (name):
            return {"name":"term name is null"}
        if not year_id:
            return {"name":"year ID cannot be null"}
        user = cast(IUserHelper,user)
        year = user.Years.filter(ID=year_id).first()
        if not year:
            return {"name":"year doesn't exist"}
        term = user.Terms.create(Year=year,Name=name)
        if term:
            return {"success":"Term Created Successfully"}
        return {"fail":"term creation faild"}
    #------------------
#------------------CLASS_ENDED#------------------