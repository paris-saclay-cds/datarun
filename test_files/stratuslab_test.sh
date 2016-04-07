#!/bin/bash
# To test datarun on stratuslab  
# Temporary tests: since no share file system, we copy before the data to the runners... To be fixed...

MASTER=$1
DR_USERNAME=$2
DR_USERPSSD=$3

python test_workflow.py http://"$MASTER" $DR_USERNAME $DR_USERPSSD
