from typing import Any
from django.core.management.base import BaseCommand

from core.models.Exams_models import Privileges
from core.services.utils.priviliages import UserPrivileges

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        # OWNER PRIVILEGES
        ownerPriv = UserPrivileges._OWNER_PRIVILEGES
        # ADMIN PRIVILEGES
        adminPriv = UserPrivileges._OWNER_PRIVILEGES
        adminPriv &= ~(UserPrivileges.CHANGE_EXAM | UserPrivileges.DELETE_EXAM | UserPrivileges.CREATE_EXAM | UserPrivileges.MERGE_EXAMS)
        # HELPER TEACHER
        helperTeacher = adminPriv | UserPrivileges.CREATE_EXAM
        # STUDENT
        student = UserPrivileges.SEE_EXAM | UserPrivileges.SOLVE_EXAM_ALLOWANCE
        Privileges.objects.create(Name="Owner",Privilege=ownerPriv)
        Privileges.objects.create(Name="Helper Teacher",Privilege=helperTeacher)
        Privileges.objects.create(Name="Admin",Privilege=adminPriv)
        Privileges.objects.create(Name="Student",Privilege=student)
    #------------------
#------------------