#!/bin/bash
# :Usage: bash deploy_runner_stratuslab.sh {fs_device} {nb_workers}
# Prepare Ubuntu (14.04) server instance for runners. 
# It starts nb_workers on the instance

cd /home/

# Mount read only disk

# Instal Packages fro the Ubuntu Repositories
sudo apt-get update; sudo apt-get upgrade
sudo apt-get install python-pip
sudo apt-get install python-numpy python-scipy
sudo pip install scikit-learn

# Install Celery
sudo pip install python-celery

# Create a user and log in with this user to run celery worker
adduser celery
mv /root/env_runner*.sh celery/.bash_aliases
mv /root/runapp celery/.
sudo -su celery 
cd celery
source .bashrc

# Run workers 
mkdir celery_info  
bash runner_workers.sh start $NB_WORKER
