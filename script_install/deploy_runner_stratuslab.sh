#!/bin/bash
# :Usage: bash deploy_runner_stratuslab.sh 
# Prepare Ubuntu (14.04) server instance for runners. 
# It starts $NB_WORKER on the instance

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
pip install numpy --upgrade
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

# Install redis
pip install redis
# Install Celery
sudo pip install celery
# Get rid of librabbitmq to force celery using python-amqp 
# https://groups.google.com/forum/#!topic/celery-users/tQolVQ7z5LA
# sudo apt-get remove python-librabbitmq

# Create a user and log in with this user to run celery worker
adduser --disabled-password --gecos "" celery

#mkdir celery
mv /root/env_runner*.sh celery/.bash_aliases
mv /root/datarun.py celery/.
#mv /root/runner_workers.sh celery/.
mv /root/supervisord_runner.conf celery/.
mv /root/celeryd*_runner.conf celery/.
mkdir celery/runapp
mv /root/tasks.py celery/runapp
mv /root/__init__.py celery/runapp
mkdir celery/celery_info  
sudo -su celery<<HERE 
cd celery
source .bash_aliases  # strange, bash_aliases not activated when log in...
echo 'if [ -f /home/celery/.bash_aliases ]; then
    . /home/celery/.bash_aliases
fi' >> .bashrc
HERE


echo $USER

# Run workers
# bash runner_workers.sh start $NB_WORKER $WORKER_QUEUES $HARD_TIME_LIMIT $SOFT_TIME_LIMIT
# Install supervisord
easy_install supervisor
# Start  celery workers and flower with supervisord
supervisord -c /home/celery/supervisord_runner.conf


cd
# Install python-netcdf4 (requires zlib, hdf5, and netCDF-C)
sudo apt-get -y install m4
wget http://zlib.net/zlib-1.2.8.tar.gz
wget https://support.hdfgroup.org/ftp/HDF5/current/src/hdf5-1.8.17.tar
wget https://github.com/Unidata/netcdf-c/archive/v4.4.1.tar.gz
tar -xzvf zlib-1.2.8.tar.gz
tar -xvf hdf5-1.8.17.tar
tar -xzvf v4.4.1.tar.gz
cd zlib-1.2.8
export ZDIR=/usr/local
./configure --prefix=${ZDIR}
sudo make check
sudo make install
cd ../hdf5-1.8.17
export H5DIR=/usr/local
./configure --with-zlib=${ZDIR} --prefix=${H5DIR}
sudo make check   # Fails here, but seems ok for netcdf
sudo make install
cd ../netcdf-c-4.4.1
export NCDIR=/usr/local
sudo CPPFLAGS=-I${H5DIR}/include LDFLAGS=-L${H5DIR}/lib ./configure --prefix=${NCDIR}
sudo make check
sudo make install  # or sudo make install
cd
sudo USE_SETUPCFG=0 pip install netcdf
pip install xarray
