#sleep infinity
python /app/manage.py migrate
python /app/manage.py clearcache
python /app/manage.py runserver 0.0.0.0:8000
