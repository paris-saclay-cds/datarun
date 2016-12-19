#!/bin/bash
# :Usage: bash deploy_master_from_image.sh 
# Prepare Ubuntu (14.04) server instance for the application deployment 
# We follow steps (+ other steps) from 
# - https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-ubuntu-14-04
# - https://gist.github.com/eezis/4026247 to install virtualenv-burrito

# Add environment variables
cd /root
source .bash_aliases

cd /home/

# Update Packages from the Ubuntu Repositories 
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" update
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade

# Mount ScienceFS disk
apt-get -y install sshfs
mkdir /mnt/datarun
sshfs -o Ciphers=arcfour256 -o allow_other -o IdentityFile=/root/.ssh/id_rsa_sciencefs -o StrictHostKeyChecking=no "$SCIENCEFS_LOGIN"@sciencefs.di.u-psud.fr:/sciencefs/homes/"$SCIENCEFS_LOGIN"/datarun /mnt/datarun
mkdir $DIR_SUBMISSION
touch $DIR_SUBMISSION/__init__.py
mkdir $DIR_DATA
touch $DIR_DATA/__init__.py

# Configure so that remote machines can connect to the master
sudo rabbitmqctl add_user $DR_DATABASE_USER $DR_DATABASE_PASSWORD
sudo rabbitmqctl add_vhost $RMQ_VHOST
sudo rabbitmqctl set_permissions -p $RMQ_VHOST $DR_DATABASE_USER ".*" ".*" ".*"
sudo service rabbitmq-server restart

# Start the worker and scheduler

# Start  celery workers and flower with supervisord
supervisord -c /home/datarun/script_install/supervisord_master.conf
# Enable apache module for reverse proxy
sudo a2enmod proxy
sudo a2enmod proxy_http


sudo chmod -R 777 $DIR_DATA
sudo chmod -R 777 $DIR_SUBMISSION

# Restart Apache
sudo service apache2 restart


