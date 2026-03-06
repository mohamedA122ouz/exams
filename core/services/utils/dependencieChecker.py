import json
from typing import cast
from django.db.models import Model
from django.db.models import Q

from core.models.Exams_models import AttachmentDependencies, WatchHistory, dependenciesRepo, solutionsSheet
from core.models import Exams_models
from core.services.types.attachmentType import AttachDependOn
from _operator import and_
from functools import reduce


class DependenciesAnalyzer:
    def __init__(self,*args, **kwargs):
        dependencies = dependenciesRepo.objects.all()
        self.ALLOWED_TABLES = {}
        self.ALLOWED_TABLES_FIELDS = {}
        for dep in dependencies:
            self.ALLOWED_TABLES.setdefault(dep.dependOnTable,getattr(Exams_models,dep.dependOnTable))
            self.ALLOWED_TABLES_FIELDS.setdefault(dep.dependOnTable,json.loads(dep.allowedFields))
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
        # self.ALLOWED_TABLES = {
        #     'solutionsSheet':solutionsSheet,
        #     'WatchHistory':WatchHistory
        # }
    #---------------
    def _fieldExtractor(self,model:Model):
        return [field.name for field in model._meta.concrete_fields]
    #---------------
    def verify(self,dep:AttachmentDependencies):
        jsonItems:AttachDependOn = cast(AttachDependOn,json.loads(dep.jsonDep))
        if not 'conditionsOnFields' in jsonItems:
            return False
        #---------------
        if not 'dependOnTable' in jsonItems:
            return False
        #---------------
        table = jsonItems['dependOnTable']
        if not table in self.ALLOWED_TABLES_FIELDS and not table in self.ALLOWED_TABLES:
            return False
        #---------------
        tableFieldsSorted = self.ALLOWED_TABLES_FIELDS[table]
        notIncludedConditions:list[str] = []
        filters = []
        for field in jsonItems['conditionsOnFields']:
            if not field in tableFieldsSorted:
                notIncludedConditions.append(field)
            #---------------
            neededResult = jsonItems['conditionsOnFields'][field]
            filters.append(Q(**{field:neededResult}))
        #---------------
        for condition in notIncludedConditions:
            field,condition = condition.split('__',1)
            neededResult = jsonItems['conditionsOnFields'][condition]
            if condition == 'gte':
                filters.append(Q(**{f"{field}__gte":neededResult}))
            #---------------
            elif condition == 'lte':
                filters.append(Q(**{f"{field}__lte":neededResult}))
            #---------------
            elif condition == 'lt':
                filters.append(Q(**{f"{field}__lt":neededResult}))
            #---------------
            elif condition == 'gt':
                filters.append(Q(**{f"{field}__gt":neededResult}))
            #---------------
            elif condition == 'contains':
                filters.append(Q(**{f"{field}__contains":neededResult}))
            #---------------
            elif condition == 'not__contains':
                filters.append(~Q(**{f"{field}__contains":neededResult}))
            #---------------
        #---------------
        Query = reduce(and_,filters)
        neededTable:Model = self.ALLOWED_TABLES[jsonItems['dependOnTable']]
        return neededTable.objects.filter(Query).exists()
    #---------------
#---------------CLASS_ENDED#---------------
