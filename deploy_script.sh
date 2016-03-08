#!/bin/bash
# :Usage: bash deploy_script.sh
# Prepare Ubuntu (14.04) server instance for the application deployment 
# We follow steps from 
# - https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-ubuntu-14-04
# - https://gist.github.com/eezis/4026247 to install virtualenv-burrito

# Install Packages from the Ubuntu Repositories 
sudo apt-get update; sudo apt-get upgrade
sudo apt-get install python-pip apache2 libapache2-mod-wsgi
sudo apt-get install git
curl -s https://raw.github.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh | $SHELL  # This command failed on AWS setup without http access
source /home/ubuntu/.venvburrito/startup.sh

# Install Postgres
sudo apt-get install python-dev libpq-dev postgresql postgresql-contrib
# Create a database for the project and a user for the database 
sudo su -postgres  # postgres: PostgreSQL administrative user.
psql -c '\i script_install/setup_database.sql'

# Clone the project
sudo git clone https://github.com/camillemarini/datarun.git

# Configure a Python Virtual Environment
mkvirtualenv datarun
sudo apt-get install python-numpy python-scipy  # is it really necessary for the master? 
pip install -Ur requirements.txt

# Complete initial project setup
cd datarun
python manage.py migrate
python manage.py collectstatic
# TODO create a superuser??

# Configure Apache: copy apache conf file to /etc/apache2/sites-available/
mv /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/backup.conf
cp script_install/000-default.conf /etc/apache2/sites-available/.

# Wrapping up some permissions issues
# I don t think we need it, since nothing has to be written in the project dir
sudo chown :www-data ~/datarun

# Restart Apache
# sudo service apache2 restart


