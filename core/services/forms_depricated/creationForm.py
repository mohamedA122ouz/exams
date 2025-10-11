from django import forms

from core.models.Exams_models import Year

class yearCreation(forms.ModelForm):
    class Meta:
        model = Year
        fields = ["Name","User"]