The idea is to build a rest api which receive submissions from databoard and train-test them.  
**Draft:**   
- a flask app receiving requests from databoard with new submissions on cv fold to be trained and tested (computation in a docker container) 
- a task queue using celery (and message broker: rabibitMQ)  
- kubernetes to manage and monitor containers deployed on several machines  

**Not ready for production environment**  

#### Databases
You have to create two Postgres databases: one for dev and on for tests.

#### Set environment variables
* `APP_SETTINGS="config.DevelopmentConfig"`  
* `DATABASE_URL`: SQLALCHEMY_DATABASE_URI for the dev database    
* `DATABASE_URL_TEST`: SQLALCHEMY_DATABASE_URI for the test database   


#### Celery
Start a celery worker before starting the application with:  
`celery worker -A datarun.celery --loglevel=info` (option `--loglevel=info` makes the logging more verbose)  
Start the application with `python manage.py runserver` (for development environment)  

#### Run in a container: NOT WORKONG YET    
install [docker-compose](https://docs.docker.com/compose/install/)   
run `docker-compose up`  
Note: for now, it does not work (I don t knwo why but the app is starting, but I get a *connection was reset* in the browser)
