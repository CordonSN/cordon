from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
comment = Table('comment', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', Text),
    Column('user_id', Integer),
    Column('post_id', Integer),
    Column('timestamp', DateTime),
)

like = Table('like', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('post_id', Integer),
    Column('timestamp', DateTime),
    Column('body', Text),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['comment'].columns['body'].create()
    pre_meta.tables['like'].columns['body'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['comment'].columns['body'].drop()
    pre_meta.tables['like'].columns['body'].create()
