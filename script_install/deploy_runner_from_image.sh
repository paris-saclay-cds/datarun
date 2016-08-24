#!/bin/bash
# :Usage: bash deploy_runner_from_image.sh 
# Prepare for runners instance started from datarun_runner image 
# It starts $1 workers on the instance with queues $2

NEW_NB_WORKER=$1
NEW_WORKER_QUEUES=$2

cd /root
# Get environment variables
cp /home/celery/.bash_aliases /root/.bash_aliases
source .bashrc
source .bash_aliases
# Modify number of workers and queues
sed -i "s/NB_WORKER=$NB_WORKER/NB_WORKER=$NEW_NB_WORKER/g" .bash_aliases
sed -i "s/WORKER_QUEUES=$WORKER_QUEUES/WORKER_QUEUES=$NEW_WORKER_QUEUES/g" .bash_aliases
source .bashrc
source .bash_aliases
cp /root/.bash_aliases /home/celery/.bash_aliases 

# Mount sciencefs disk
sshfs -o Ciphers=arcfour256 -o allow_other -o IdentityFile=/root/.ssh/id_rsa_sciencefs -o StrictHostKeyChecking=no "$SCIENCEFS_LOGIN"@sciencefs.di.u-psud.fr:/sciencefs/homes/"$SCIENCEFS_LOGIN"/datarun /mnt/datarun

# Start workers
supervisord -c /home/celery/supervisord_runner.conf
