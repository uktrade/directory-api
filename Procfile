web: python manage.py migrate --noinput && python manage.py distributed_elasticsearch_migrate && waitress-serve --port=$PORT conf.wsgi:application
celery_worker: celery -A conf worker -l info
celery_beat: celery -A conf beat -l info -S django
