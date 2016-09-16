#!/bin/bash -xe

webserver_cmd="gunicorn -c /usr/src/app/gunicorn/conf.py data.wsgi --log-file - -b [::1]:8000 -b 0.0.0.0:8000"
queue_worker_cmd="python /usr/src/app/manage.py queue_worker"

# If values are not set, default to true on both
if [ -z ${WEB_SERVER_ENABLED+x} ] && [ -z ${QUEUE_WORKER_ENABLED+x} ]
then
    export WEB_SERVER_ENABLED=true
    export QUEUE_WORKER_ENABLED=true
fi

if [ "$WEB_SERVER_ENABLED" == "true" ] && [ "$QUEUE_WORKER_ENABLED" == "true" ]
then
    echo "Starting web server and queue worker"
    eval $webserver_cmd &
    eval $queue_worker_cmd
else
    if [ "$WEB_SERVER_ENABLED" == "true" ]
    then
        echo "Starting web server"
        eval $webserver_cmd
    else
        echo "Web server not enabled"
    fi

    if [ "$QUEUE_WORKER_ENABLED" == "true" ]
    then
        eval $queue_worker_cmd
    else
        echo "Queue worker not enabled"
    fi
fi
