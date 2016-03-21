#!/bin/bash 
# :Usage: bash script_install/runner_workers.sh {start|stop|restart} {nb_local_workers}
# Starting/stopping/restarting nb_local_workers  

rm -r celery_info/*

export REMOTE_WORKERS=""
for i in `seq 1 $3`;
do
    export REMOTE_WORKERS=("$REMOTE_WORKERS lw$i"); 
done    
                                                
if [ $1 = "stop" ]; then
    echo "Stopping the workers";
    # Local workers
    celery multi $1 $REMOTE_WORKERS --pidfile="$(pwd)/celery_info/%n.pid";
else
    echo "$1 the workers";
    # Local workers and starting the scheduler
    celery multi $1 $REMOTE_WORKERS -l INFO -A celeryremote \
        --logfile="$(pwd)/celery_info/%n.log" \
        --pidfile="$(pwd)/celery_info/%n.pid";
fi
