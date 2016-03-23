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

TODO

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
