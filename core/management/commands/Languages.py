from typing import Any
from django.core.management.base import BaseCommand

from core.models.Exams_models import ProfileSettings

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        profileSettings = [ProfileSettings(
            PreferedLang=i,User_id=None
        ) for i in ["EN","AR"]]
        ProfileSettings.objects.bulk_create(profileSettings)

    #------------------
#------------------