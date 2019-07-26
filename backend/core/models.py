import datetime
from django.db import models


# Create your models here.

class Query(models.Model):
    query = models.CharField(max_length=255)
    ip = models.CharField(max_length=16)
    date = models.DateTimeField(auto_now=True)
    total_result = models.BigIntegerField()

class QueryResult(models.Model):
    ordinal_number = models.PositiveSmallIntegerField()
    link = models.CharField(max_length=255)
    word = models.CharField(max_length=255)
    query = models.ForeignKey('Query', on_delete=models.CASCADE)