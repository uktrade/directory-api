from api.celery import app
from company.models import Company


@app.task
def save_company_to_elasticsearch(company_id):
    company = Company.objects.get(pk=company_id)
    company.to_doc_type().save()
