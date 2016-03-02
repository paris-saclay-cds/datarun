#!/bin/bash
# :Usage: bash run_test.sh -d 
# Test the workflow of datarun: data submission, models submission, 
# train-test models, and save in the datarun database
# A test database is created and destroyed if the -d flag is specified

# Set up some environment variables
export DIR_DATA="test_data"
export DIR_SUBMISSION="test_submission"
rm -r $DIR_DATA/*
rm -r $DIR_SUBMISSION/*
touch $DIR_SUBMISSION/__init__.py

# Create a test database
export DR_DATABASE_NAME="test_datarun"
createdb $DR_DATABASE_NAME
# Apply migrations
python manage.py migrate

# Create a test user
python manage.py createuser MrTest test@test.com test 

# Start celery workers
# TODO

# Run a test server in the background
python manage.py runserver 127.0.0.1:8000

