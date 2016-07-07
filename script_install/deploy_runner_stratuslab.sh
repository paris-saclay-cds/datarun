#!/bin/bash
# :Usage: bash deploy_runner_stratuslab.sh {fs_device} {nb_workers}
# Prepare Ubuntu (14.04) server instance for runners. 
# It starts nb_workers on the instance

cd /home/
export LC_ALL=en_US.UTF-8
export LANGUAGE=en_US.UTF-8


# Update Packages from the Ubuntu Repositories 
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" update
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade
# Install pip
curl -O https://bootstrap.pypa.io/get-pip.py
python get-pip.py
pip install pyopenssl ndg-httpsclient pyasn1
# Install Ubuntu dependencies for Python
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install build-essential python-dev
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install gfortran
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install swig
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install libatlas-dev
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install liblapack-dev
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install libfreetype6 libfreetype6-dev
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install libxft-dev
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install pandoc
# Install numpy, scipy, and ipython
pip install numpy
pip install scipy
pip install pandas
pip install ipython
pip install scikit-learn
# Install git 
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install git
# Install xgboost
cd; git clone --recursive https://github.com/dmlc/xgboost
cd xgboost; make -j4
cd python-package; sudo python setup.py install
cd /home/


# Mount SienceFS disk
source /root/env_runner.sh
apt-get -y install sshfs
mkdir /mnt/datarun
sshfs -o Ciphers=arcfour256 -o allow_other -o IdentityFile=/root/.ssh/id_rsa_sciencefs -o StrictHostKeyChecking=no "$SCIENCEFS_LOGIN"@sciencefs.di.u-psud.fr:/sciencefs/homes/"$SCIENCEFS_LOGIN"/datarun /mnt/datarun

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
bash runner_workers.sh start $NB_WORKER $WORKER_QUEUES
