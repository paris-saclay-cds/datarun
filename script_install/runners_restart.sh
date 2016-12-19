#! /bin/bash
# :Usage: bash runners_restart.sh {file_runner} 
# To restart all runners from a list of runners mentionneed in {file_runner} 
# {file_runner} is a text file containing in each line 
# the address of the runner and the number of workers to start on it

echo $(pwd)
if ! [[ $(pwd) == *"script_install" ]]; 
then
    echo "you are not in the script_install directory... Go to this directory and rerun the script!";
    exit 1; 
fi

FILE_RUNNERS=$1

while read p; do
    set -- $p
    ADD_RUNNER=$1
    echo "** Restarting Runner: $ADD_RUNNER **";
    ssh -o "StrictHostKeyChecking no" root@"$ADD_RUNNER" 'bash -s' < singlerunner_restart.sh; 

done < $FILE_RUNNERS
