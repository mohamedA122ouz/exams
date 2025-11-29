from typing import Any, Optional, cast
from core.services.userHelper import IUserHelper


class YearService:
    def createYear(self,user,yearName:Optional[str])->dict[str,str]:
        if yearName == None:
            return {"name":"cannot be null"}
        tempUser = cast(IUserHelper,user)
        if tempUser.Years.filter(Name=yearName).exists():
            return {"name":"cannot create two years with the same name"}
        year = tempUser.Years.create(Name=yearName)
        if year:
            return {"success":"created successfully"}
        return {"fail":"created faild"}
    #------------------
    def showYears(self,user)->list[dict[str,Any]]:
        user = cast(IUserHelper,user)
        years = user.Years.values()
        return list(years)
    #------------------
#------------------CLASS_ENDED#------------------