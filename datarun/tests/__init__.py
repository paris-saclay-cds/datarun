import os
from datarun import app, db

test_app = app.test_client()
app.config.from_object('datarun.config.TestingConfig')
# to initiate the database, is it ok to just use createdb or shall we use what
# is here https://github.com/kelsmj/flask-test-example

database_test_name = os.getenv('DATABASE_URL_TEST').split('/')[-1]
dir_data_test = 'test_data'
dir_submission_test = 'test_submission'
os.environ['DATABASE_TEST_NAME'] = database_test_name
os.environ['DIR_DATA_TEST'] = dir_data_test
os.environ['DIR_SUBMISSION_TEST'] = dir_submission_test


def init_db():
    """Initialisation of a test database"""
# Not sure that the following lines are necessary
#    try:
#        os.system('dropdb ' + database_test_name)
#    except:
#        pass
#    os.system('createdb ' + database_test_name)
#    os.system('python manage.py db upgrade')
    db.session.close()
    db.drop_all()
    db.create_all()


#def teardown():
#    try:
#        os.system('dropdb ' + database_test_name)
#    except:
#        print('test database does not exist')
#

init_db()
try:
    os.mkdir(dir_data_test)
except:
    print('Data test directory already exists')
try:
    os.mkdir(dir_submission_test)
except:
    print('Submission test directory already exists')
