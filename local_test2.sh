#!/bin/bash
# :Usage: bash local_test2.sh -d 
# **Must be run after local_test1.sh**
# Test the workflow of datarun: data submission, models submission, 
# train-test models, and save in the datarun database
# A test database is created.
# If the -d flag is specified, the test database is destroyed and workers are killed

# Set up some environment variables
export DR_DATABASE_NAME="test_datarun"

# Test workflow: send data, split train test, send submission 
cd test_files
python test_workflow.py 
cd ..

# Destroy database and reset environment variables to original values
while getopts ":d" opt; do
  case $opt in
    d)
      echo "Destroying the test database and reseting it to original value";
      dropdb $DR_DATABASE_NAME;
      echo "Killing the workers";
      ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9;
      ps auxww | grep 'celerybeat' | awk '{print $2}' | xargs kill -9;
      ;;
    \?)
      echo "Invalid option: -$OPTARG" 
      ;;
  esac
done


