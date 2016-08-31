from __future__ import absolute_import
import os
from celery import Celery

broker_url = 'amqp://%s:%s@%s/%s' % (os.environ.get('DR_DATABASE_USER'),
                                     os.environ.get('DR_DATABASE_PASSWORD'),
                                     os.environ.get('IP_MASTER'),
                                     os.environ.get('RMQ_VHOST'))
backend_url = 'redis://:%s@%s:6379/0' %\
    (os.environ.get('DR_DATABASE_PASSWORD'), os.environ.get('IP_MASTER'))
app = Celery('datarun', backend=backend_url,
             broker=broker_url)
app.conf.CELERY_TASK_SERIALIZER = 'json'
app.conf.CELERY_RESULT_SERIALIZER = 'json'

app.autodiscover_tasks(['runapp'], force=True)
