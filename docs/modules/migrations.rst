.. _migrations:

How to deal with migrations?
============================

If you modify the app models, you'll need to migrate the database.


1. modify ``runapp/models.py``
2. run ``python manage.py makemigrations`` which will create a migrations file in ``runapp/migrations/``     
3. apply the migration with ``python manage.py migrate``  
4. add the migrations file to your git and commit both the modified ``runapp/models.py`` and migrations file (so that other contributors can have the migration history)

