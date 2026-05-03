from email.policy import default
from typing import Type

from core.services.types.questionType import QuestionEase, QuestionType, ScoringMode
from core.models.Exams_models import Question,Lecture
from rest_framework import serializers
from django.db.models import Model




class QuestionFromFront_Serializer(serializers.ModelSerializer[Question]):
    # Use names that match your QuestionFromFront TypedDict exactly
    answers = serializers.CharField(source='Ans',required=False)
    question = serializers.CharField(source='Text_Url')
    type = serializers.ChoiceField(source="Type",choices=QuestionType.choices())
    ease = serializers.ChoiceField(source='Ease', choices=QuestionEase.choices())
    scoringMode = serializers.ChoiceField(choices=ScoringMode.choices(),default=ScoringMode.DEFAULT)
    # Logic-only fields (not in Model)
    choices = serializers.ListField(child=serializers.CharField(), required=False, default=list,read_only=True)
    attachments = serializers.ListField(child=serializers.DictField(), required=False, default=list,read_only=True)
    
    # We use the ID directly to keep the parser simple
    lecture_id = serializers.PrimaryKeyRelatedField(
        queryset=Lecture.objects.all(),
        source='Lecture' # DRF will fetch the Lecture object automatically
    )

    class Meta: #type:ignore
        model = Question
        fields = [
            'ID',
            'answers',
            'question',
            'type',
            'ease',
            'scoringMode',
            'choices',
            'attachments',
            'OwnedBy',
            'createdAt',
            'lecture_id'
        ]
        read_only_fields = ['ID','choices','attachments','createdAt','OwnedBy']
    #---------------
    
#---------------