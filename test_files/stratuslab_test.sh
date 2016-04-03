#!/bin/bash
# To test datarun on stratuslab  
# Temporary tests: since no share file system, we copy before the data to the runners... To be fixed...

MASTER=$1
DR_USERNAME=$2
DR_USERPSSD=$3

################################################################
# To be removed when we have a shared file system
#WORKER1=$4
#WORKER2=$5
#for WORKER in $WORKER1 $WORKER2 
#do
#    ssh root@$WORKER << EOF
#      mkdir /home/celery/data
#      mkdir /home/celery/submission
#EOF
#    scp -r ../test_data/* root@$WORKER:/home/celery/data/.
#    scp -r ../test_submission/* root@$WORKER:/home/celery/submission/.
#done
################################################################

python test_workflow http://"$MASTER" $DR_USERNAME $DR_USERPSSD
