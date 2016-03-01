#!/bin/bash
# :Usage: bash run_test.sh -d 
# Test the workflow of datarun: data submission, models submission, 
# train-test models, and save in the datarun database
# A test database is created and destroyed if the -d flag is specified


# Send data
echo "{"name": "iris", "target_column": "species", "workflow_elements": "classifier", "files": {"iris.csv": $(cat test_files/iris.csv)}}"

curl -u "MrTest":"test" -H "Content-Type: application/json" -X POST -d '{"name": "iris", "target_column": "species", "workflow_elements": "classifier", "files": {"iris.csv": "$(cat test_files/iris.csv)"}}' http://127.0.0.1:8000/runapp/rawdata/
#"files": {"iris.csv": "aa"}}' http://127.0.0.1:8000/runapp/rawdata/

curl -u "MrTest":"test" -X GET http://127.0.0.1:8000/runapp/rawdata/

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
