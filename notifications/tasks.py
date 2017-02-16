from api.celery import app
from notifications import notifications


@app.task
def daily_notifications(self):
    notifications.no_case_studies()
    notifications.hasnt_logged_in()
    notifications.verification_code_not_given()


@app.task
def weekly_notifications(self):
    notifications.new_companies_in_sector()
