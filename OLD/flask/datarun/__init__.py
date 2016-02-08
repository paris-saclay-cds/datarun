import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from celery import Celery

app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTINGS'))
db = SQLAlchemy(app)
app.config['CELERY_BROKER_URL'] = 'amqp://'
app.config['CELERY_RESULT_BACKEND'] = 'amqp://'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

import datarun.views
