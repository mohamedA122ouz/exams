from typing import Any
from django.core.management.base import BaseCommand
from core.models.Exams_models import paymentLocker

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        paymentLocker.objects.create(
            totalAmount=0,
            count=0
        )
    #---------------
#---------------