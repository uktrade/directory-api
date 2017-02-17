from api.celery import app
from api.distributed_lock import distributed_lock
from notifications import notifications


@app.task
def no_case_studies():
    with distributed_lock('no_case_studies'):
        notifications.no_case_studies()


@app.task
def hasnt_logged_in():
    with distributed_lock('hasnt_logged_in'):
        notifications.hasnt_logged_in()


@app.task
def verification_code_not_given():
    with distributed_lock('verification_code_not_given'):
        notifications.verification_code_not_given()


@app.task
def new_companies_in_sector():
    with distributed_lock('new_companies_in_sector'):
        notifications.new_companies_in_sector()
