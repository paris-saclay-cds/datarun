#! /bin/bash
# :Usage: bash scp_runner_stratuslab.sh {file_runner} {private_key_file}
# To scp to a stratuslab instance (Ubuntu 14.04) files needed to deploy runners 
# {file_runner} is a text file containing in each line 
# the address of the runner and the number of workers to start on it
# and {private_key_file} file of the private key to connect to ScienceFS account (with absolute path)

echo $(pwd)
if ! [[ $(pwd) == *"script_install" ]]; 
then
    echo "you are not in the script_install directory... Go to this directory and rerun the script!";
    exit 1; 
fi

FILE_RUNNERS=$1
SCIENCEFS_KEY=$2

mkdir tmp_runner
while read p; do
    set -- $p
    ADD_RUNNER=$1
    NB_WORKER=$2
    WORKER_QUEUES=$3
    HARD_TIME_LIMIT=$4
    SOFT_TIME_LIMIT=$5
    echo "** Runner: $ADD_RUNNER with $NB_WORKER workers for queues $WORKER_QUEUES **"
    # Make it possible to log in as root
    ssh ubuntu@"$ADD_RUNNER" 'bash -s' < root_permissions.sh
    # Copy sciencefs key and install scipt
    scp $SCIENCEFS_KEY root@"$ADD_RUNNER":/root/.ssh/id_rsa_sciencefs
    scp deploy_runner_stratuslab.sh datarun.py runner_workers.sh \
        ../runapp/tasks.py ../runapp/__init__.py root@"$ADD_RUNNER":/root/.
    cp env_runner.sh tmp_runner/env_runner.sh
    sed -i "$ a export NB_WORKER=$NB_WORKER" tmp_runner/env_runner.sh
    sed -i "$ a export WORKER_QUEUES=$WORKER_QUEUES" tmp_runner/env_runner.sh
    sed -i "$ a export HARD_TIME_LIMIT=$HARD_TIME_LIMIT" tmp_runner/env_runner.sh
    sed -i "$ a export SOFT_TIME_LIMIT=$SOFT_TIME_LIMIT" tmp_runner/env_runner.sh
    scp tmp_runner/env_runner.sh root@"$ADD_RUNNER":/root/.
    # Install runners
    ssh root@"$ADD_RUNNER" 'bash -s' < deploy_runner_stratuslab.sh;
done < $FILE_RUNNERS

rm -r tmp_runner
