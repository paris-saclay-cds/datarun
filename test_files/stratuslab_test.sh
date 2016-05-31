#!/bin/bash
# To test datarun on stratuslab  

MASTER=$1
DR_USERNAME=$2
DR_USERPSSD=$3

python test_workflow.py http://"$MASTER" $DR_USERNAME $DR_USERPSSD
