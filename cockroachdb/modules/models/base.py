from peewee import Model

from cockroachdb.modules.connection import database


class BaseModel(Model):
    class Meta:
        database = database
