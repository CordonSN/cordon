import os
basedir = os.path.abspath(os.path.dirname(__file__))

# ----- Standard
CSRF_ENABLED = True
SECRET_KEY = 'asdfghjkl'
# ----- Template
TEMPLATE = 'cordon'
# ----- Database
SQLALCHEMY_DATABASE_URI = 'postgresql://USERNAME:PASSOWRD@DOMANIN/DATABASE_NAME'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
# pagination
POSTS_PER_PAGE = 10
FRIENDS_PER_PAGE = 5
