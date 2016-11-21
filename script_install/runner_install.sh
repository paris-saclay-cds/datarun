#! /bin/bash
# :Usage: bash runner_install.sh {file_runner} {package_name}
# To install {package_name} to a list of runners mentionneed in {file_runner} 
# {file_runner} is a text file containing in each line 
# the address of the runner and the number of workers to start on it

echo $(pwd)
if ! [[ $(pwd) == *"script_install" ]]; 
then
    echo "you are not in the script_install directory... Go to this directory and rerun the script!";
    exit 1; 
fi

FILE_RUNNERS=$1
PACKAGE_NAME=$2

echo "pip install $PACKAGE_NAME" > temp_install.sh

while read p; do
    set -- $p
    ADD_RUNNER=$1
    echo "** $PACKAGE_NAME for Runner: $ADD_RUNNER **";
    ssh -o "StrictHostKeyChecking no" root@"$ADD_RUNNER" 'bash -s' < temp_install.sh; 

done < $FILE_RUNNERS
rm temp_install.sh
