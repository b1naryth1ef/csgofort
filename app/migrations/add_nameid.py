from database import *
from playhouse.migrate import *

def pre(): pass
def post(): pass

migrator = PostgresqlMigrator(db)

def run():
    migrate(
        migrator.add_column('marketitem', 'nameid', MarketItem.nameid),
    )
