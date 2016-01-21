The idea is to build a rest api which receive submissions from databoard and train-test them.  
**Draft:**   
- a flask app receiving requests from databoard with new submissions on cv fold to be trained and tested (computation in a docker container) 
- a task queue using celery (and message broker: rabibitMQ)  
- kubernetes to manage and monitor containers deployed on several machines  

#### Databases
You have to create two Postgres databases: one for dev and on for tests.

#### Set environment variables
* `APP_SETTINGS="config.DevelopmentConfig"`  
* `export DATABASE_URL`: for the dev database    
* `export DATABASE_URLTEST`: for the test database    
