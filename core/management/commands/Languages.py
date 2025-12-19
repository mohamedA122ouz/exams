from typing import Any
from django.core.management.base import BaseCommand

from core.models.Exams_models import supportedLanguages

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        profileSettings = [supportedLanguages(
            Name=i
        ) for i in ["EN","AR"]]
        supportedLanguages.objects.bulk_create(profileSettings)
    #------------------
#------------------