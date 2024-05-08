from django.db import models


class Energy(models.Model):
    username = models.CharField(max_length=100) 
    date = models.BigIntegerField() 
    kwh = models.FloatField()
