#!/bin/bash 
# :Usage: celery_workers {start|stop|restart} {nb_remote_workers} {nb_local_workers}
# Starting/stopping/restarting nb_remote_workers workers remotely (TODO) 
# with two different queues: low and high
# and nb_local_workers locally for the scheduler 

rm -r celery_info/*

export REMOTE_WORKERS=""
for i in `seq 1 $2`;
do
    export REMOTE_WORKERS=("$REMOTE_WORKERS rw$i"); 
done    
export LOCAL_WORKERS=""
for i in `seq 1 $3`;
do
    export LOCAL_WORKERS=("$LOCAL_WORKERS lw$i"); 
done    
                                                
if [ $1 = "stop" ]; then
    echo "Stopping the workers";
    # Remote workers TODO (for now we create them locally to test) 
    celery multi $1 $REMOTE_WORKERS --pidfile="$(pwd)/celery_info/%n.pid";
    # Local workers
    celery multi $1 $LOCAL_WORKERS --pidfile="$(pwd)/celery_info/%n.pid";
else
    echo "$1 the workers";
    # Remote workers TODO (for now we create them locally to test) 
    export W1=$(expr $2 / 2);
    export W2=$(expr $W1 + 1);
    celery multi $1 $REMOTE_WORKERS -l INFO -A datarun -Q:1-$W1 low -Q:$W2-$2 high \
        --logfile="$(pwd)/celery_info/%n.log" \
        --pidfile="$(pwd)/celery_info/%n.pid"; 
    # Local workers and starting the scheduler
    celery multi $1 $LOCAL_WORKERS -l INFO -A datarun \
        --logfile="$(pwd)/celery_info/%n.log" \
        --pidfile="$(pwd)/celery_info/%n.pid";
    celery -A datarun beat -s "$(pwd)/celery_info/celerybeat-schedule"

fi
