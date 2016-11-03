#!/bin/bash -xe

python /usr/src/app/manage.py migrate
python /usr/src/app/manage.py collectstatic --noinput
gunicorn api.wsgi --bind [::1]:$PORT --bind 0.0.0.0:$PORT --log-file -
