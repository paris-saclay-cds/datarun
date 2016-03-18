#!/bin/bash
# :Usage: bash deploy_script.sh
# Prepare Ubuntu (14.04) server instance for the application deployment 
# We follow steps from 
# - https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-ubuntu-14-04
# - https://gist.github.com/eezis/4026247 to install virtualenv-burrito

# Add environment variables
# env.sh file with environment variables must be in the same folder as this script
mv env.sh ~/.bash_aliases
source .bashrc

# Set locales variables
export LC_ALL=en_US.UTF-8
export LANGUAGE=en_US.UTF-8

cd /home/

# Install Packages from the Ubuntu Repositories 
sudo apt-get update; sudo apt-get upgrade
sudo apt-get install python-pip apache2 libapache2-mod-wsgi
sudo apt-get install git
wget https://raw.github.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh
bash virtualenv-burrito.sh 
source /home/.venvburrito/startup.sh

# Clone the project
sudo git clone https://github.com/camillemarini/datarun.git
cd datarun

# Install Postgres
sudo apt-get install python-dev libpq-dev postgresql postgresql-contrib
pg_createcluster 9.3 main --start
# Change postgres permissions
sed -i "85c local   all             postgres                                trust" /etc/postgresql/9.3/main/pg_hba.conf 
sudo service postgresql restart
# Create a database for the project and a user for the database 
psql -U postgres -c '\i script_install/setup_database.sql'
# Change database user permissions
sed -i "86i local   all             $DR_DATABASE_USER                                 trust" /etc/postgresql/9.3/main/pg_hba.conf
sudo service postgresql restart

# Configure a Python Virtual Environment
mkvirtualenv datarun
sudo apt-get install python-numpy python-scipy  # is it really necessary for the master? 
pip install -Ur requirements.txt

# Complete initial project setup
python manage.py migrate
python manage.py collectstatic
python manage.py createuser $DR_DATABASE_USER $DR_DATABASE_PASSWORD $DR_EMAIL --superuser

# Install RabbitMQ 
sudo apt-get install rabbitmq-server
# Configure so that remote machines can connect to the master
sudo rabbitmqctl add_user $DR_DATABASE_USER $DR_DATABASE_PASSWORD
sudo rabbitmqctl add_vhost $RMQ_VHOST
sudo rabbitmqctl set_permissions -p $RMQ_VHOST $DR_DATABASE_USER ".*" ".*" ".*"
sudo service rabbitmq-server restart

# Start the worker and scheduler
bash script_install/master_workers.sh start $NB_LOCAL_WORKER

# Configure Apache: copy apache conf file to /etc/apache2/sites-available/
mv /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/backup.conf
cp script_install/stratuslab-default.conf /etc/apache2/sites-available/000-default.conf

# Deal with environment variables
sed 's/=/ /g' ~/.bash_aliases > tt.txt
sed "s/'//g" tt.txt > tt1.txt
sed "s/export/SetEnv/g" tt1.txt > tt.txt
while read p; 
do   
    sed -i "22a $p" /etc/apache2/sites-available/000-default.conf; 
done < tt.txt
sed -i "s/SetEnv/    SetEnv/g" /etc/apache2/sites-available/000-default.conf
rm tt.txt tt1.txt

# Wrapping up some permissions issues
# I don t think we need it, since nothing has to be written in the project dir
sudo chown :www-data ../datarun
sudo chown :www-data ../.
# To make it works we have to set it to sudo chown www-data ../. but then we cannot connect in ssh to it. Maybe we can try to put datarun in another forlder such as home?...

# Restart Apache
sudo service apache2 restart


