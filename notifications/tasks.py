from django.core.cache import cache

from conf.celery import app
from notifications import notifications


def lock_acquired(lock_name):
    """ Returns False if the lock was already set in the last 20 hours

    Multiple celery beat schedulers are running at the same time, which
    results in duplicated scheduled tasks. Cache-lock mechanism is used to
    assure that only one task gets executed. Lock expires after 20 hours

    """
    return cache.add(lock_name, 'acquired', 72000)


def verification_code_not_given():
    if lock_acquired('verification_code_not_given'):
        notifications.verification_code_not_given()


@app.task
def new_companies_in_sector():
    if lock_acquired('new_companies_in_sector'):
        notifications.new_companies_in_sector()
