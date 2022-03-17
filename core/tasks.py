from django.core.management import call_command

from conf.celery import app


@app.task()
def elsaticsearch_migrate():
    call_command('elasticsearch_migrate')
