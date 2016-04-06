#!/bin/bash 
# :Usage: bash script_install/runner_workers.sh {start|stop|restart} {nb_local_workers} {queue_names}
# Starting/stopping/restarting nb_local_workers for queues queue_names
# ex:  bash script_install/runner_workers.sh start 2 L,celery

rm -r celery_info/*

export REMOTE_WORKERS=""
for i in `seq 1 $2`;
do
    export REMOTE_WORKERS=("$REMOTE_WORKERS lw$i"); 
done    
export WQ=$(echo $REMOTE_WORKERS | tr " " ,)

if [ $1 = "stop" ]; then
    echo "Stopping the workers";
    # Local workers
    celery multi $1 $REMOTE_WORKERS --pidfile="$(pwd)/celery_info/%n.pid";
else
    echo "$1 the workers";
    # Local workers and starting the scheduler
    celery multi $1 $REMOTE_WORKERS -l INFO -A datarun -Q:$WQ $3 \
        --logfile="$(pwd)/celery_info/%n.log" \
        --pidfile="$(pwd)/celery_info/%n.pid";
fi
