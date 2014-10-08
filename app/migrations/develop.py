"""
This file contains any migrations that need to be run from one develop
release to another. This will generally get cleared out weekly, and is
really only used for deployments.
"""

from database import *
from maz.mazdb import *
from playhouse.migrate import *

migrator = PostgresqlMigrator(db)

def add_user_indexes():
    migrate(
        migrator.add_index("user", ("steamid", ), True)
    )

def pre(): pass
def post(): pass

def run():
    add_user_indexes()
