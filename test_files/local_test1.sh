#!/bin/bash
# :Usage: bash local_test1.sh  
# Set up test environment: creation of a test database, starting the workers,
# and running a development server
# local_test2.sh must be run afterward

cd ..

# Set up some environment variables
export DIR_DATA="test_data"
export DIR_SUBMISSION="test_submission"
export CELERY_SCHEDULER_PERIOD='*/1'
export RMQ_VHOST='test'
export IP_MASTER='localhost'
rm -r $DIR_DATA/*
rm -r $DIR_SUBMISSION/*
touch $DIR_DATA/__init__.py
touch $DIR_SUBMISSION/__init__.py

# Create a test database
export DR_DATABASE_NAME="test_datarun"
createdb $DR_DATABASE_NAME
# Apply migrations
python manage.py migrate

# Create a test user
python manage.py createuser MrTest test@test.com test 

# Set up RabbitMQ
sudo rabbitmqctl add_user $DR_DATABASE_USER $DR_DATABASE_PASSWORD
sudo rabbitmqctl add_vhost $RMQ_VHOST
sudo rabbitmqctl set_permissions -p $RMQ_VHOST $DR_DATABASE_USER ".*" ".*" ".*"
sudo service rabbitmq-server restart

# Start celery workers
bash test_files/cmd_workers_local.sh start 2 1

# Run a test server in the background
python manage.py runserver 127.0.0.1:8000

