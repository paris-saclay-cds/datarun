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
    ssh -o "StrictHostKeyChecking no" ubuntu@"$ADD_RUNNER" 'bash -s' < root_permissions.sh
    # Copy sciencefs key and install scipt
    scp $SCIENCEFS_KEY root@"$ADD_RUNNER":/root/.ssh/id_rsa_sciencefs
    scp deploy_runner_stratuslab.sh supervisord_runner.conf env_runner.sh root@"$ADD_RUNNER":/root/. 
    scp datarun.py ../runapp/tasks.py ../runapp/__init__.py root@"$ADD_RUNNER":/root/.
    cp celeryd_runner.conf tmp_runner/celeryd_runner.conf
    sed -i -e "s/CONCURRENCY/$NB_WORKER/g" tmp_runner/celeryd_runner.conf
    sed -i -e "s/VAR_QUEUES/$WORKER_QUEUES/g" tmp_runner/celeryd_runner.conf
    sed -i -e "s/VAR_HARD_TIME_LIMIT/$HARD_TIME_LIMIT/g" tmp_runner/celeryd_runner.conf
    sed -i -e "s/VAR_SOFT_TIME_LIMIT/$SOFT_TIME_LIMIT/g" tmp_runner/celeryd_runner.conf
    scp tmp_runner/celeryd_runner.conf root@"$ADD_RUNNER":/root/.
    # Install runners
    ssh -o "StrictHostKeyChecking no" root@"$ADD_RUNNER" 'bash -s' < deploy_runner_stratuslab.sh;
done < $FILE_RUNNERS

rm -r tmp_runner
