from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
post = Table('post', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', String),
    Column('timestamp', DateTime),
    Column('user_id', Integer),
    Column('capo', String),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=128)),
    Column('nickname', String(length=64)),
    Column('email', String(length=120)),
    Column('role', SmallInteger, default=ColumnDefault(0)),
    Column('sex', String(length=128)),
    Column('slogan', String(length=128)),
    Column('status', String(length=128)),
    Column('location', String(length=128)),
    Column('bio', Text),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].columns['capo'].drop()
    post_meta.tables['user'].columns['bio'].create()
    post_meta.tables['user'].columns['location'].create()
    post_meta.tables['user'].columns['name'].create()
    post_meta.tables['user'].columns['sex'].create()
    post_meta.tables['user'].columns['slogan'].create()
    post_meta.tables['user'].columns['status'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].columns['capo'].create()
    post_meta.tables['user'].columns['bio'].drop()
    post_meta.tables['user'].columns['location'].drop()
    post_meta.tables['user'].columns['name'].drop()
    post_meta.tables['user'].columns['sex'].drop()
    post_meta.tables['user'].columns['slogan'].drop()
    post_meta.tables['user'].columns['status'].drop()
