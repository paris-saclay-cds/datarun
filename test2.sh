#!/bin/bash
# :Usage: bash run_test.sh -d 
# Test the workflow of datarun: data submission, models submission, 
# train-test models, and save in the datarun database
# A test database is created and destroyed if the -d flag is specified


# Test workflow: send data, split train test, send submission 
cd test_files
python test_workflow.py 
cd ..

# Destroy database and reset environment variables to original values
while getopts ":d" opt; do
  case $opt in
    d)
      echo "Destroying the test database and reseting it to original value"
      dropdb $DR_DATABASE_NAME
      ;;
    \?)
      echo "Invalid option: -$OPTARG" 
      ;;
  esac
done
