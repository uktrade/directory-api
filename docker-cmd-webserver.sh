#!/bin/bash -xe

python /usr/src/app/manage.py migrate
gunicorn -c /usr/src/app/gunicorn/conf.py api.wsgi --bind 0.0.0.0:$PORT --log-file -
