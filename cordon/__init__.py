import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from config import basedir

# ----- Application
cordon = Flask(__name__)
cordon.config.from_object('config')
# ----- Database
db = SQLAlchemy(cordon)
# ----- Login System
lm = LoginManager()
lm.init_app(cordon)
lm.login_view = 'login'

from cordon import views, models

if not cordon.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/cordon.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    cordon.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    cordon.logger.addHandler(file_handler)
    cordon.logger.info('microblog startup')
