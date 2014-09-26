from elasticsearch import Elasticsearch
from peewee import *
from playhouse.postgres_ext import *
import redis

db = PostgresqlExtDatabase('fort', user="b1n", password="b1n", threadlocals=True, port=5433)
red = redis.Redis()
es = Elasticsearch()