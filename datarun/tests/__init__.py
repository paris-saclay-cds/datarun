import os
from datarun import app, db

test_app = app.test_client()
app.config.from_object('datarun.config.TestingConfig')


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
#    db.session.remove()
#    db.drop_all()

init_db()
try:
    os.mkdir(os.getenv('DIR_DATA'))
except:
    os.system('rm -rf ' + os.getenv('DIR_DATA') + '/boson')
    print('Data test directory already exists')
try:
    os.system('rm -rf ' + os.getenv('DIR_SUBMISSION') + '/*')
    os.mkdir(os.getenv('DIR_SUBMISSION'))
except:
    print('Submission test directory already exists')
