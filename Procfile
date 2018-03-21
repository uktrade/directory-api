web: python manage.py distributed_migrate --noinput && python manage.py distributed_elasticsearch_migrate && waitress-serve --port=$PORT api.wsgi:application
celery_worker: celery -A api worker -l info
celery_beat: celery -A api beat -l info -S django
