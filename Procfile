web: python manage.py distributed_migrate --noinput && python manage.py distributed_elasticsearch_migrate && gunicorn conf.wsgi:application --bind 0.0.0.0:$PORT
celery_worker: python manage.py distributed_migrate --noinput && celery -A conf worker -l info
celery_beat: python manage.py distributed_migrate --noinput && celery -A conf beat -l info -S django
