.._troubleshooting

Troubleshooting
===============

How to check runners are running?
---------------------------------

In the root datarun folder, run ``celery -A datarun status``.   


How to get by hands the results of a task?
------------------------------------------

Run in Python:
::

    from runapp import tasks
    t = tasks.<name_of_the_task>.AsyncResult('<task_id>')
    print(t.state)  
    print(t.get())

The ``task_id`` is printed when you send the task to datarun. For databoard users, it can be retrieved in the log of the databoard worker.  


