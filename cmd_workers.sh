#!/bin/bash 
# :Usage: celery_workers {start|stop|restart} {nb_celery_node}
# Starting/stopping/restarting nb_celery_node workers 
# with two different queues: low and high

export LIST_WORKERS=""
for i in `seq 1 $2`;
do
    export LIST_WORKERS=("$LIST_WORKERS worker$i"); 
done    
                                                
if [ $1 = "stop" ]; then
    echo "Stopping the workers";
    celery multi $1 $LIST_WORKERS --pidfile="$(pwd)/celery_info/%n.pid";
else
    echo "$1 the workers";
    export W1=$(expr $2 / 2);
    export W2=$(expr $W1 + 1);
    celery multi $1 $LIST_WORKERS -l INFO -A datarun -Q:1-$W1 low -Q:$W2-$2 high \
        --logfile="$(pwd)/celery_info/%n.log" \
        --pidfile="$(pwd)/celery_info/%n.pid"; 
fi
