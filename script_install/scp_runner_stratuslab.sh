#! /bin/bash
# :Usage: bash scp_runner_stratuslab.sh {file_runner}
# To scp to a stratuslab instance (Ubuntu 14.04) files needed to deploy runners 
# {file_runner} is a text file containing in each line 
# the address of the runner and the number of workers to start on it

FILE_RUNNERS=$1

mkdir tmp_runner
while read p;
do
    set -- $p
    ADD_RUNNER=$1
    NB_WORKER=$2
    echo "** Runner: $ADD_RUNNER with $NB_WORKER workers **"
    scp deploy_runner_stratuslab.sh root@"$ADD_RUNNER":/root/.
    scp celeryremote.py root@"$ADD_RUNNER":/root/.
    scp runner_workers.sh root@"$ADD_RUNNER":/root/.
    scp -r ../runapp root@"$ADD_RUNNER":/root/.
    cp env_runner.sh tmp_runner/env_runner.sh
    sed -i "$ a export NB_WORKER=$NB_WORKER" tmp_runner/env_runner.sh
    scp tmp_runner/env_runner.sh root@"$ADD_RUNNER":/root/.
done < $FILE_RUNNERS

rm -r tmp_runner
