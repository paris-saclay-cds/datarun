### How to use it?

The API documentation can be found at [http://host/docs/](http://127.0.0.1:8000/docs/) (you need to be logged-in to see it).  

### How to run it (locally)?

#### 1. Install the application

Clone the project: `git clone https://github.com/camillemarini/datarun.git`  
Install dependencies (might be useful to create a virtual environment before, eg using [virtualenv and virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/)):  
`pip install -r requirements.txt`.   
For numpy and scipy(for Unbuntu & Debian users):  
`sudo apt-get install python-numpy python-scipy`  

#### 2. Set up the database
  
Datarun uses a Postgres database. 
Before starting, [install postgres](http://www.postgresql.org/download/) if needed and create a database with `createdb database_name`.   

#### 3. Define environment variables

* `DR_DATABASE_NAME`: database name  
* `DR_DATABASE_USER`: database user name  
* `DR_DATABASE_PASSWORD`: database user password 

If your are using virtualenvwrapper, you can store these variables in `$VIRTUAL_ENV/bin/postactivate`

#### 4. Apply migrations

Run: `python manage.py migrate`

#### 5. Create a superuser

Run: `python manage.py createsuperuser`  

#### 6. Run the server (localhost)

Run: `python manage.py runserver`

#### 7. Start celery worker 

Run: `celery -A datarun worker -l info`

### How to test it?

Run: `python manage.py test`

### Migrations

If you modify the app models, you'll need to migrate the database.  
1. modify `runapp/models.py`  
2. run `python manage.py makemigrations`, which will create a migrations file in `runapp/migrations/` 
3. apply the migration with `python manage.py migrate`  
4. add the migrations file to your git and commit both the modified `runapp/models.py` and migrations file (so that other contributors can have the migration history)    



