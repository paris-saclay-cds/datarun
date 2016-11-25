.. _deployment:

-  `How to run it locally?`_
-  `How to run it on stratuslab openstack?`_


How to run it locally?
~~~~~~~~~~~~~~~~~~~~~~

1. Install the application
^^^^^^^^^^^^^^^^^^^^^^^^^^

Clone the project:
``git clone https://github.com/camillemarini/datarun.git`` 

Install dependencies (might be useful to create a virtual environment before, eg
using `virtualenv and virtualenvwrapper`_): 

1. For numpy, scipy, and pandas (for Unbuntu & Debian users): 
   ``sudo apt-get install python-numpy python-scipy python-pandas``   
2. ``pip install -r requirements.txt``  

Install RabbitMQ (celery `broker`_):
``sudo apt-get install rabbitmq-server``

Install Redis and set it up for our app (celery `result backend`_):  

    ::
    sudo apt-get install -y redis-server
    pip install redis
    sudo sed -i "331a requirepass $DR_DATABASE_PASSWORD" /etc/redis/redis.conf
    sudo service redis-server restart


2. Set up the database
^^^^^^^^^^^^^^^^^^^^^^

Datarun uses a Postgres database. Before starting, `install postgres`_
if needed and create a database with ``createdb database_name``.

3. Define environment variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  ``DR_WORKING_ENV``: ``PROD`` for production environment or ``DEV``
   for development env
-  ``DIR_DATA``: directory where to save data  
-  ``DIR_SUBMISSION``: directory where to save submissions  
-  ``DR_DATABASE_NAME``: database name
-  ``DR_DATABASE_USER``: database user name
-  ``DR_DATABASE_PASSWORD``: database user password (do not use special
   characters)
-  ``DR_EMAIL``: email for the platform superuser
-  ``CELERY_SCHEDULER_PERIOD``: period (in min) at which the scheduler
   checks new trained models and saves them in the database. Ex: ``*/2``
   for every 2 min.
-  ``RMQ_VHOST``: RabbitMQ vhost name
-  ``IP_MASTER``: ip address of the master, here: ``localhost``

If your are using virtualenvwrapper, you can store these variables in
``$VIRTUAL_ENV/bin/postactivate``

4. Apply migrations
^^^^^^^^^^^^^^^^^^^

Run: ``python manage.py migrate``

5. Create a superuser
^^^^^^^^^^^^^^^^^^^^^

Run: ``python manage.py createsuperuser``

6. Run the server (localhost)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run: ``python manage.py runserver``

7. Start celery worker and scheduler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run: ``bash test_files/cmd_workers.sh start 2 1`` for 3 workers, of
which one is for the scheduler Note: to start one worker, run:
``celery -A datarun worker -l info``


How to run it on stratuslab openstack?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../../datarun.png
    :width: 600px
    :align: center
    :alt: oups!


There are two possibilities:   

A. from scratch using an Ubuntu 14.04 image on openstack, or on any other cloud.   
B. using images ``datarun_master`` and ``datarun_runner`` on openstack  

Note: in both cases, you need a scienceFS account. On your scienceFS
disk, create in the root directory a folder called ``datarun``.

A. Using an Ubuntu 14.04 image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A1. Start one instance for the master and as many instances as you want for the runners.
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Use Ubuntu v14.04 images. For the master, an VM os.2 is enough.

A2. Go to the ``script_install`` directory and stay there while configuring the master and runners.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

A3. Configure the master
''''''''''''''''''''''''

-  On your local computer, create a file called ``env.sh`` (do not
   change this name) with the content below. 
   Do not forget to change the values and be careful **not to commit this file** :-) 
   And **do not add comments to the file**.  
   Make sure that the directory ``SCIENCEFS_DATARUN`` has been created on the sciencefs disk beforehand.  

   ::

       export SCIENCEFS_LOGIN='login_for_scienceFS_account'
       export SCIENCEFS_DATARUN='path_of_sciencefs_disk'
       export DR_DATABASE_NAME='database_name'
       export DR_DATABASE_USER='database_user'
       export DR_DATABASE_PASSWORD='database_password'
       export DIR_DATA='/mnt/datarun/data'
       export DIR_SUBMISSION='/mnt/datarun/submission'
       export USER_LOGIN='user_name'
       export USER_PSWD='user_password'
       export CELERY_SCHEDULER_PERIOD='*/2'
       export DR_EMAIL='mail@emailworld.com'
       export RMQ_VHOST='rabbitMQ_vhost_name'
       export IP_MASTER=$(/sbin/ifconfig eth0 | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}')

-  Run:

   ::

       bash scp_master_stratuslab.sh master_address scienceFS_private_key

   with ``master_address`` being the master server address (e.g.,
   ``onevm-81.lal.in2p3.fr``) and ``scienceFS_private_key`` being the
   file name (with absolute path) of the private key to connect to
   ScienceFS account. This will scp to the master some files that are
   needed to configure the master.

-  Ssh to the instance and run:

   ::

       bash deploy_master_stratuslab.sh
       source ~/.bashrc

-  Once you've checked that the app is running (going to <master_address>/admin for instance), do not forget to change the Django setting ``DEBUG`` to False and add the server name (<IP_MASTER>) in ``ALLOWED_HOSTS`` (preceded with a dot). In ``/home/datarun/datarun/settings.py``:

   ::

       DEBUG = False
       ALLOWED_HOSTS = ['.<IP_MASTER>']

A4. Configure runners
'''''''''''''''''''''

-  On your local computer in the folder ``script_install``, create a
   file called ``env_runner.sh`` (be careful to use the name
   ``env_runner.sh``) with the content below. Do not forget to change
   the values and **be careful not to commit this file** :-) And **do not add
   comments to the file**.  
   Make sure that the directory ``SCIENCEFS_DATARUN`` has been created on the sciencefs disk beforehand.  

   ::

       export SCIENCEFS_LOGIN='login_for_scienceFS_account'
       export SCIENCEFS_DATARUN='path_of_sciencefs_disk'
       export DR_DATABASE_USER='database_name'
       export DR_DATABASE_PASSWORD='database_password'
       export DIR_DATA='/mnt/datarun/data'
       export DIR_SUBMISSION='/mnt/datarun/submission'
       export RMQ_VHOST='rabbitMQ_vhost_name'
       export IP_MASTER='xxx.yyy.zz.aaa'

   Values of these environment variables must be the same as what you
   defined in ``env.sh``, they are used to connect to the master and
   read data from it.

-  On your local computer, create a file ``list_runners.txt`` containing
   the list of runners address address, the number of tasks you want to be run 
   concurrently on each runner, the list of queues processed by the workers (at least
   one of each among ``L``, ``H``, ``celery``), and the hard and soft
   time limit in seconds:

   ::

       address_runner_1 number_task_runner_1 list_queues_1 hard_time_limit_1 soft_time_limit_1
       address_runner_2 number_task_runner_2 list_queues_2 hard_time_limit_2 soft_time_limit_2
       ...
       address_runner_3 number_task_runner_3 list_queues_3 hard_time_limit_3 soft_time_limit_3

   Example:

   ::

       134.158.75.112 2 L,celery 360 300
       134.158.75.113 3 H 240 200

-  Run:

   ::

       bash scp_runner_stratuslab.sh list_runners.txt scienceFS_private_key

   As above, ``scienceFS_private_key`` is the file name (with absolute
   path) of the private key to connect to ScienceFS account. This will
   scp some files to the runners and configure them (by executing the
   script ``deploy_runner_stratuslab.sh``)

You should now be ready to use datarun on stratuslab!



B. Using images ``datarun_master`` and ``datarun_runner`` on openstack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

B1. Start one instance for the master and as many instances as you want for the runners.
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Use the image ``datarun_master`` for the master and ``datarun_runner``
for runners.

B2. Go to the ``script_install`` directory and stay there while configuring the master and runners.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

B3. Configure master
''''''''''''''''''''

1. Ssh to the instance
2. Go to ``/home/datarun/script_install``
3. Run ``bash deploy_master_from_image.sh``

B4. Configure runners
'''''''''''''''''''''

-  On your local computer, create a file ``list_runners.txt`` containing
   the list of runners address address, the number of taskss you want be run 
   concurrently on each runner, the list of queues processed by the workers (at least
   one of each among ``L``, ``H``, ``celery``), and the hard and soft
   time limit in seconds:

   ::

       address_runner_1 number_task_runner_1 list_queues_1 hard_time_limit_1 soft_time_limit_1
       address_runner_2 number_task_runner_2 list_queues_2 hard_time_limit_2 soft_time_limit_2
       ...
       address_runner_3 number_task_runner_3 list_queues_3 hard_time_limit_3 soft_time_limit_3

   Example:

   ::

       134.158.75.112 2 L,celery 360 300
       134.158.75.113 3 H 240 200

-  Run:

   ::
        bash scp_runner_from_image.sh list_runners.txt
   
   This will configure the runners (by executing the script
   ``deploy_runner_from_image.sh``). **Check that the sciencefs disk has
   been correclty mounted** (ssh to the instance and check if
   ``/mnt/datarun`` is not empty), sometimes it fails…


.. _virtualenv and virtualenvwrapper: https://virtualenvwrapper.readthedocs.org/en/latest/
.. _broker: http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#rabbitmq
.. _result backend: http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
.. _install postgres: http://www.postgresql.org/download/


C. How to install missing packages on runners
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the package can be installed with pip, run: ``runner_install {list_runner.txt} {package name}`` with ``{list_runner.txt}`` being the file mentionned (A and B sections) specifying runners. It is going to run on each runner the following ``pip install {package_name}``
