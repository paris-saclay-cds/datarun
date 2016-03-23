from __future__ import absolute_import
import os
from celery import Celery

broker_url = 'amqp://%s:%s@%s/%s' % (os.environ.get('DR_DATABASE_USER'),
                                     os.environ.get('DR_DATABASE_PASSWORD'),
                                     os.environ.get('IP_MASTER'),
                                     os.environ.get('RMQ_VHOST'))
app = Celery('datarun', backend='amqp',
             broker=broker_url)


app.autodiscover_tasks(['runapp'], force=True)
