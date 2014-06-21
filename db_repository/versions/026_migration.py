from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=128)),
    Column('nickname', String(length=64)),
    Column('password', String(length=64)),
    Column('email', String(length=120)),
    Column('show_email', Boolean),
    Column('role', SmallInteger, default=ColumnDefault(0)),
    Column('cover', Binary),
    Column('sex', String(length=128)),
    Column('slogan', String(length=128)),
    Column('status', String(length=128)),
    Column('location', String(length=128)),
    Column('bio', Text),
    Column('last_seen', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['cover'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['cover'].drop()
