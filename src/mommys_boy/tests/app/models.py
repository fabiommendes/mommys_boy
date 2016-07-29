from datetime import date
from django.db import models
from mommys_boy import DjangoMommyFactory


class TestModel(models.Model):
    first_name = models.CharField(max_length=50)
    some_number = models.IntegerField()
    some_date = models.DateField()


class TestFactory(DjangoMommyFactory):
    class Meta:
        model = TestModel
        recipe = 'global'

    some_number = 42


class TestFactoryUnix(DjangoMommyFactory):
    class Meta:
        model = TestModel
        recipe = 'unix-time'

    some_date = date(1970, 1, 1)
