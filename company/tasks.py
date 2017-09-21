from api.celery import app
from company import models


@app.task
def save_company_to_elasticsearch(pk):
    company = models.Company.objects.get(pk=pk)
    company.to_doc_type().save()


@app.task
def save_case_study_to_elasticsearch(pk):
    case_study = models.CompanyCaseStudy.objects.get(pk=pk)
    case_study.to_doc_type().save()
