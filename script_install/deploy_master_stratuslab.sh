#!/bin/bash
# :Usage: bash deploy_master_stratuslab.sh 
# Prepare Ubuntu (14.04) server instance for the application deployment 
# We follow steps (+ other steps) from 
# - https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-ubuntu-14-04
# - https://gist.github.com/eezis/4026247 to install virtualenv-burrito

# Add environment variables
# env.sh file with environment variables must be in the same folder as this script
mv env.sh ~/.bash_aliases
echo 'export LC_ALL=en_US.UTF-8' >> ~/.bash_aliases
echo 'export LANGUAGE=en_US.UTF-8' >> ~/.bash_aliases
source .bash_aliases

cd /home/

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
# Install Apache and mod_wsgi
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install apache2 libapache2-mod-wsgi
# Install Apache module for flower (apache as a reverse proxy)
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install libapache2-mod-proxy-html libxml2-dev
# Install git 
sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install git
# Install numpy, scipy, and ipython
pip install numpy
pip install scipy
pip install pandas
pip install ipython
pip install scikit-learn

# Mount ScienceFS disk
apt-get -y install sshfs
mkdir /mnt/datarun
sshfs -o Ciphers=arcfour256 -o allow_other -o IdentityFile=/root/.ssh/id_rsa_sciencefs -o StrictHostKeyChecking=no "$SCIENCEFS_LOGIN"@sciencefs.di.u-psud.fr:/sciencefs/homes/"$SCIENCEFS_LOGIN"/datarun /mnt/datarun
mkdir $DIR_SUBMISSION
touch $DIR_SUBMISSION/__init__.py
mkdir $DIR_DATA
touch $DIR_DATA/__init__.py

# Clone the project
sudo git clone https://github.com/camillemarini/datarun.git
cd datarun

# Install Postgres
sudo apt-get -y install libpq-dev postgresql postgresql-contrib
pg_createcluster 9.3 main --start
# Change postgres permissions
sed -i "85c local   all             postgres                                trust" /etc/postgresql/9.3/main/pg_hba.conf 
sudo service postgresql restart
# Create a database for the project and a user for the database 
# CHECK: Got pb with password once, but could not reproduce the error
psql -U postgres -c '\i script_install/setup_database.sql'
# To avoid pb...TODO understand why setup_database.sql fails for the password
psql -U postgres -c "ALTER ROLE $DR_DATABASE_USER WITH PASSWORD '$DR_DATABASE_PASSWORD'"
# Change database user permissions
sed -i "86i local   all             $DR_DATABASE_USER                                 trust" /etc/postgresql/9.3/main/pg_hba.conf
sudo service postgresql restart

# Install required Python packages
pip install -r requirements.txt

# Complete initial project setup
python manage.py migrate
python manage.py collectstatic
python manage.py createuser $DR_DATABASE_USER $DR_EMAIL $DR_DATABASE_PASSWORD --superuser

# Install redis
sudo apt-get install redis-server
sudo pip install redis
sed -i "331a requirepass $DR_DATABASE_USER" /etc/redis/redis.conf 
sed -i 's/bind 127.0.0.1/# bind 127.0.0.1/g' /etc/redis/redis.conf 
sudo service redis-server restart 

# Install RabbitMQ 
sudo apt-get install -y rabbitmq-server
# Configure so that remote machines can connect to the master
sudo rabbitmqctl add_user $DR_DATABASE_USER $DR_DATABASE_PASSWORD
sudo rabbitmqctl add_vhost $RMQ_VHOST
sudo rabbitmqctl set_permissions -p $RMQ_VHOST $DR_DATABASE_USER ".*" ".*" ".*"
sudo service rabbitmq-server restart

# Start the worker and scheduler
mkdir celery_info
rm celery_info/*
chmod -R 777 celery_info
# bash script_install/master_workers.sh start $NB_LOCAL_WORKER

# Install supervisord
easy_install supervisor
# Start  celery workers and flower with supervisord
supervisord -c /home/datarun/script_install/supervisord_master.conf
# Enable apache module for reverse proxy
sudo a2enmod proxy
sudo a2enmod proxy_http

# Configure Apache: copy apache conf file to /etc/apache2/sites-available/
mv /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/backup.conf
cp script_install/stratuslab-default.conf /etc/apache2/sites-available/000-default.conf

# Deal with environment variables
sed 's/=/ /g' ~/.bash_aliases > tt.txt
sed "s/'//g" tt.txt > tt1.txt
sed "s/export/SetEnv/g" tt1.txt > tt.txt
while read p; 
do  
   if ! [[ $p == *"IP_MASTER"* ]];
   then 
     sed -i "22a $p" /etc/apache2/sites-available/000-default.conf; 
   else
     sed -i "22a SetEnv IP_MASTER $IP_MASTER" /etc/apache2/sites-available/000-default.conf;
   fi;
done < tt.txt
sed -i "s/SetEnv/    SetEnv/g" /etc/apache2/sites-available/000-default.conf
rm tt.txt tt1.txt

# Wrapping up some permissions issues
# I don t think we need it, since nothing has to be written in the project dir
sudo chown -R www-data:www-data ../datarun
sudo chown :www-data ../.
sudo chmod -R 777 $DIR_DATA
sudo chmod -R 777 $DIR_SUBMISSION
# To make it works we have to set it to sudo chown www-data ../. but then we cannot connect in ssh to it. Maybe we can try to put datarun in another forlder such as home?...

# Restart Apache
sudo service apache2 restart


