.. _tests:

Tests
=====

for django tests
^^^^^^^^^^^^^^^^

Run: ``python manage.py test``

for local celery tests
^^^^^^^^^^^^^^^^^^^^^^

Run in one terminal: ::

    cd test_files; bash local_test1.sh 

Run in another terminal: ::

    cd test_files; bash local_test2.sh -d 

It creates a database, start celery workers, and run tests from ``test_files/test_workflow.py`` file.

If two ‘Oh yeah’ are printed, tests are ok!

for tests on stratuslab
^^^^^^^^^^^^^^^^^^^^^^^

Run: ::

    cd test_files 
    bash stratuslab_test.sh master_address username password

with ``master_address`` being the master server address (e.g.,
``onevm-81.lal.in2p3.fr``), ``username`` being a datarun user, and
``password`` its password. 

It runs tests from ``test_files/test_workflow.py`` file. 

If two ‘Oh yeah’ are printed, tests are ok!


