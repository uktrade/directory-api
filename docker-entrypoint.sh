#!/bin/bash -xe

python /usr/src/app/manage.py migrate
gunicorn -c /usr/src/app/gunicorn/conf.py data.wsgi --log-file - -b [::1]:8000 -b 0.0.0.0:8000

