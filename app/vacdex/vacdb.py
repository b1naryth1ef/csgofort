from peewee import *
from playhouse.postgres_ext import *

db = PostgresqlExtDatabase('fort', user="b1n", password="b1n", threadlocals=True, port=5433)

class BModel(Model):
    class Meta:
        database = db

class VacBan(object):
    steamid = IntegerField()
    discovered = DateTimeField()