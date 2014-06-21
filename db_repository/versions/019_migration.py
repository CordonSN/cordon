from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('nickname', String),
    Column('email', String),
    Column('role', SmallInteger),
    Column('bio', Text),
    Column('location', String),
    Column('name', String),
    Column('sex', String),
    Column('slogan', String),
    Column('status', String),
    Column('last_login', DateTime),
    Column('password', String),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=128)),
    Column('nickname', String(length=64)),
    Column('password', String(length=64)),
    Column('email', String(length=120)),
    Column('role', SmallInteger, default=ColumnDefault(0)),
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
    pre_meta.tables['user'].columns['last_login'].drop()
    post_meta.tables['user'].columns['last_seen'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['last_login'].create()
    post_meta.tables['user'].columns['last_seen'].drop()
