#!/bin/bash
# :Usage: bash deploy_runner_stratuslab.sh {fs_device} {nb_workers}
# Prepare Ubuntu (14.04) server instance for runners. 
# It starts nb_workers on the instance

cd /home/
export LC_ALL=en_US.UTF-8
export LANGUAGE=en_US.UTF-8

# Mount disk

# Instal Packages fro the Ubuntu Repositories
sudo apt-get -y update 
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install python-pip
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install python-numpy python-scipy python-pandas
sudo pip install scikit-learn

# Install Celery
sudo pip install celery
# Get rid of librabbitmq to force celery using python-amqp 
# https://groups.google.com/forum/#!topic/celery-users/tQolVQ7z5LA
# sudo apt-get remove python-librabbitmq

# Create a user and log in with this user to run celery worker
adduser --disabled-password --gecos "" celery

#mkdir celery
mv /root/env_runner*.sh celery/.bash_aliases
#mv /root/env_runner*.sh /root/.bash_aliases
mv /root/datarun.py celery/.
mv /root/runner_workers.sh celery/.
mkdir celery/runapp
mv /root/tasks.py celery/runapp
mv /root/__init__.py celery/runapp
sudo -su celery 
cd celery
source .bash_aliases  # strange, bash_aliases not activated when log in...
#source /root/.bash_aliases

# Run workers
mkdir celery_info  
bash runner_workers.sh start $NB_WORKER
