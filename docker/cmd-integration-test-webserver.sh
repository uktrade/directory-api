#!/bin/bash -xe

python /usr/src/app/manage.py migrate --noinput
python /usr/src/app/manage.py loaddata test_fixtures/load_tests.json
python /usr/src/app/manage.py collectstatic --noinput
gunicorn api.wsgi --bind [::1]:$PORT --bind 0.0.0.0:$PORT --log-file -
