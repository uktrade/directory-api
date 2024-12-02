web: python manage.py collectstatic --noinput && python manage.py distributed_migrate --noinput && python manage.py distributed_elasticsearch_migrate && gunicorn conf.wsgi:application --config conf/gunicorn.py --bind 0.0.0.0:$PORT --worker-connections 1000
celery_worker: python manage.py distributed_migrate --noinput && celery -A conf worker -l info
celery_beat: python manage.py distributed_migrate --noinput && celery -A conf beat -l info -S django
