from peewee_migrate import Router
from peewee import SqliteDatabase

import bin.Config as Config


# Load config right at the start
config = Config.load_config()

db = SqliteDatabase(config['Database'])

def migrate():
    router = Router(db)
    router.run()

# Create migration
#router.create('initial')

# Run migration/migrations
#router.run('initial')

# Run all unapplied migrations

