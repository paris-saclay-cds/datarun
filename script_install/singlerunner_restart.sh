#!/bin/bash
# :Usage: bash restart_workers.sh
# Kill and restart runners 

ps auxww | grep 'supervisor' | awk '{print $2}' | xargs kill -9 
ps auxww | grep 'celery' | awk '{print $2}' | xargs kill -9
source /home/celery/.bash_aliases
supervisord -c /home/celery/supervisord_runner.conf
