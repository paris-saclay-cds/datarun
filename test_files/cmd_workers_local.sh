#!/bin/bash 
# :Usage: cmd_workers {start|stop|restart} {nb_remote_workers} {nb_local_workers}
# Starting/stopping/restarting nb_remote_workers workers, locally in fact for tests 
# with two different queues: low (L) and high (H)
# and nb_local_workers locally for the scheduler 

rm -r celery_info/*

export REMOTE_WORKERS=""
for i in `seq 1 $2`;
do
    export REMOTE_WORKERS=("$REMOTE_WORKERS rw$i"); 
done    
export LOCAL_WORKERS=""
export LOCAL_WORKERS_Q=""
for i in `seq 1 $3`;
do
    export LOCAL_WORKERS=("$LOCAL_WORKERS lw$i"); 
done    
export LOCAL_WORKERS_Q=$(echo $LOCAL_WORKERS | tr " " ,)                                                
if [ $1 = "stop" ]; then
    echo "Stopping the workers";
    # Remote workers (here we create them locally to test) 
    celery multi $1 $REMOTE_WORKERS --pidfile="$(pwd)/celery_info/%n.pid";
    # Local workers
    celery multi $1 $LOCAL_WORKERS --pidfile="$(pwd)/celery_info/%n.pid";
else
    echo "$1 the workers";
    # Remote workers (here we create them locally to test) 
    export W1=$(expr $2 / 2);
    export W2=$(expr $W1 + 1);
    export WQL="rw1"
    export WQH="rw$W2"
    if [[ $W1 > 1 ]];
    then
        for i in `seq 2 $W1`;
        do
            export WQL=("$WQL,rw$i")
        done
        for i in `seq $(expr $W2 + 1) $2`;
        do
            export WQH=("$WQH,rw$i")
        done
    fi
    celery multi $1 $REMOTE_WORKERS -l INFO -A datarun -Q:$WQL L,celery -Q:$WQH H \
        --logfile="$(pwd)/celery_info/%n.log" \
        --pidfile="$(pwd)/celery_info/%n.pid"; 
    # Local workers and starting the scheduler
    celery multi $1 $LOCAL_WORKERS -l INFO -A datarun -Q:$LOCAL_WORKERS_Q master_periodic \
        --logfile="$(pwd)/celery_info/%n.log" \
        --pidfile="$(pwd)/celery_info/%n.pid";
    celery -A datarun beat -s "$(pwd)/celery_info/celerybeat-schedule" \
        --pidfile="$(pwd)/celery_info/celerybeat.pid" --detach

fi
