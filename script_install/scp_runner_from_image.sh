#! /bin/bash
# :Usage: bash scp_runner_stratuslab.sh {file_runner} 
# To deploy runner on a datarun_runner image
# {file_runner} is a text file containing in each line 
# the address of the runner and the number of workers to start on it

echo $(pwd)
if ! [[ $(pwd) == *"script_install" ]]; 
then
    echo "you are not in the script_install directory... Go to this directory and rerun the script!";
    exit 1; 
fi

FILE_RUNNERS=$1

mkdir tmp_runner
while read p; do
    set -- $p
    ADD_RUNNER=$1
    NB_WORKER=$2
    WORKER_QUEUES=$3
    echo "** Runner: $ADD_RUNNER with $NB_WORKER workers for queues $WORKER_QUEUES **"
    # Make it possible to log in as root
    ssh ubuntu@"$ADD_RUNNER" 'bash -s' < root_permissions.sh
    # Install runners
    ssh root@"$ADD_RUNNER" 'bash -s' < deploy_runner_from_image.sh "$NB_WORKER" "$WORKER_QUEUES";
done < $FILE_RUNNERS

rm -r tmp_runner
