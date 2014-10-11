from peewee import *
from playhouse.migrate import *

class SimpleMigration(object):
    def run(self): pass

class PostgresqlFortMigrator(PostgresqlMigrator):
    @operation
    def pre_add_enum(self, field):
        field.pre_field_create()
        return SimpleMigration()

    @operation
    def post_add_enum(self, field):
        field.post_field_create()
        return SimpleMigration()
