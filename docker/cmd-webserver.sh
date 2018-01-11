#!/bin/bash -xe

python /usr/src/app/manage.py distributed_migrate --noinput
python /usr/src/app/manage.py ensure_elasticsearch_indices
python /usr/src/app/manage.py collectstatic --noinput
gunicorn api.wsgi --bind 0.0.0.0:$PORT --log-file -
