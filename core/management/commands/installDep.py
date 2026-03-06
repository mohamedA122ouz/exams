import json
from typing import Any
from django.core.management.base import BaseCommand

from core.models.Exams_models import dependenciesRepo, supportedLanguages

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        #---------------#-----------
        # EXAMPLE TO WHAT IS THE OUTPUT
        #---------------#-----------
        # self.ALLOWED_TABLES_FIELDS = {
        #     'solutionsSheet':[
        #         'TotalMark'
        #         'Exam__ID'
        #     ],
        #     'WatchHistory':['attachment']
        # }
        items = []
        items.append(
            dependenciesRepo(
                dependentTable='ClassRoomAttachment',
                dependOnTable='solutionsSheet',
                allowedFields=json.dumps([
                    'TotalMark',
                    'Exam__ID'
                ])
            )
        )
        items.append(
            dependenciesRepo(
                dependentTable='ClassRoomAttachment',
                dependOnTable='WatchHistory',
                allowedFields=json.dumps([
                    'attachment'
                ])
            )
        )
        
        dependenciesRepo.objects.bulk_create(items)
    #---------------
#---------------