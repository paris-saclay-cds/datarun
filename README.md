## Datarun

* [How to use it?](#how-to-use-it)
* [How to run it locally?](#how-to-run-it-locally)
* [How to run it on stratuslab?](#how-to-run-it-on-stratuslab)
* [How to test it?](#how-to-test-it)

### How to use it?

The API documentation can be found at [http://host/docs/](http://127.0.0.1:8000/docs/) 
(you need to be logged-in to see it, you can log in via the admin page).  

### How to run it (locally)?

#### 1. Install the application

Clone the project: `git clone https://github.com/camillemarini/datarun.git`  
Install dependencies (might be useful to create a virtual environment before, eg using [virtualenv and virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/)):  
1. For numpy, scipy, and pandas (for Unbuntu & Debian users): `sudo apt-get install python-numpy python-scipy python-pandas`  
2. `pip install -r requirements.txt`.   

Install RabbitMQ (celery [broker](http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#rabbitmq)): `sudo apt-get install rabbitmq-server`   

#### 2. Set up the database
  
Datarun uses a Postgres database. 
Before starting, [install postgres](http://www.postgresql.org/download/) if needed and create a database with `createdb database_name`.   

#### 3. Define environment variables

* `DR_WORKING_ENV`: `PROD` for production environment or `DEV` for development env
* `DR_DATABASE_NAME`: database name  
* `DR_DATABASE_USER`: database user name  
* `DR_DATABASE_PASSWORD`: database user password (do not use special characters)   
* `DR_EMAIL`: email for the platform superuser     
* `CELERY_SCHEDULER_PERIOD`: period (in min) at which the scheduler checks new trained models and saves them in the database. Ex: `*/2` for every 2 min.    
* `NB_LOCAL_WORKER`: number of celery workers for the scheduler   
* `RMQ_VHOST`: RabbitMQ vhost name     
* `IP_MASTER`: ip address of the master, here: `localhost`   


If your are using virtualenvwrapper, you can store these variables in `$VIRTUAL_ENV/bin/postactivate`

#### 4. Apply migrations

Run: `python manage.py migrate`

#### 5. Create a superuser

Run: `python manage.py createsuperuser`  

#### 6. Run the server (localhost)

Run: `python manage.py runserver`

#### 7. Start celery worker and scheduler 

Run: `bash test_files/cmd_workers.sh start 2 1` for 3 workers, of which one is for the scheduler  
Note: to start one worker, run: `celery -A datarun worker -l info`  


### How to run it on stratuslab?

TODO add figure

##### 1. Start one instance for the master and as many instances as you want for the runners.  
Use the image `BJILII-tFu00rKKM-enj9l83rsn` which corresponds to Ubuntu v14.04 x86_64.    
```
stratus-run-instance BJILII-tFu00rKKM-enj9l83rsn --cpu=2 --ram=4000
```

##### 2. Go to the `script_install` directory and stay there while configuring the master and runners.

##### 3. Configure the master

* On your local computer, create a file called `env.sh` (do not change this name) with the content below.  
Do not forget to change the values and be careful not to commit this file :-)  
And do not add comments to the file.     
```
export DR_DATABASE_NAME='database_name'
export DR_DATABASE_USER='database_user'
export DR_DATABASE_PASSWORD='database_password'
export DIR_DATA='data'
export DIR_SUBMISSION='submission'
export USER_LOGIN='user_name'
export USER_PSWD='user_password'
export CELERY_SCHEDULER_PERIOD='*/2' 
export NB_LOCAL_WORKER=1
export DR_EMAIL='mail@emailworld.com'
export RMQ_VHOST='rabbitMQ_vhost_name'
export IP_MASTER=$(/sbin/ifconfig eth0 | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}')
```   

* Run `bash scp_master_stratuslab.sh master_address` with `master_address` being the master server address (e.g., `onevm-81.lal.in2p3.fr`)   
This will scp to the master some files that are needed to configure the master.  

* Ssh to the instance and run `bash deploy_master_stratuslab.sh`.   
For now, we have to execute the command from the instance, since it is asking for many parameters. TODO: make changes so that we can run the script with ssh from our local machine.   
 
##### 4. Configure runners

* On your local computer in the folder `script_install`, create a file called `env_runner.sh` (be careful to use the name `env_runner.sh`) with the content below.  
Do not forget to change the values and be careful not to commit this file :-)  
And do not add comments to the file.
```
export DIR_DATA='data'
export DIR_SUBMISSION='submission'
export RMQ_VHOST='rabbitMQ_vhost_name'
export IP_MASTER='xxx.yyy.zz.aaa'
# NB_WORKER added by scp_runner_stratuslab.sh
```

* On your local computer, create a file `list_runners.txt` containing the list of runners address address and the number of workers you want on each runner:  
```
address_runner_1 number_worker_runner_1  
address_runner_2 number_worker_runner_2  
...
address_runner_3 number_worker_runner_3  
```  

* Run `bash scp_runner_stratuslab.sh list_runners.txt`.  
This will scp some files to the runners and configure them (by executing the script `deploy_runner_stratuslab.sh`)  

You should now be ready to use datarun on stratuslab!  

### How to test it?

#### for django tests
Run: `python manage.py test`

#### for local celery tests
Run in one terminal: `cd test_files; bash local_test1.sh`  
Run in another terminal: `cd test_files; bash local_test2.sh -d`  
If two 'Oh yeah' are printed, tests are ok!     

### Migrations

If you modify the app models, you'll need to migrate the database.  
1. modify `runapp/models.py`  
2. run `python manage.py makemigrations`, which will create a migrations file in `runapp/migrations/` 
3. apply the migration with `python manage.py migrate`  
4. add the migrations file to your git and commit both the modified `runapp/models.py` and migrations file (so that other contributors can have the migration history)    
