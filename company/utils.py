import datetime

from elasticsearch_dsl import Index, analyzer

from django.conf import settings
from django.utils import timezone

from company import search
from company.stannp import stannp_client


def send_verification_letter(company):
    recipient = {
        'postal_full_name': company.postal_full_name,
        'address_line_1': company.address_line_1,
        'address_line_2': company.address_line_2,
        'locality': company.locality,
        'country': company.country,
        'postal_code': company.postal_code,
        'po_box': company.po_box,
        'custom_fields': [
            ('full_name', company.postal_full_name),
            ('company_name', company.name),
            ('verification_code', company.verification_code),
            ('date', datetime.date.today().strftime('%d/%m/%Y')),
            ('company', company.name),
        ]
    }

    stannp_client.send_letter(
        template=settings.STANNP_VERIFICATION_LETTER_TEMPLATE_ID,
        recipient=recipient
    )

    company.is_verification_letter_sent = True
    company.date_verification_letter_sent = timezone.now()
    company.save()


def rebuild_and_populate_elasticsearch_index(CompanyModel):
    indices = (
        (search.COMPANY_INDEX_NAME, search.CompanyDocType),
        (search.CASE_STUDY_INDEX_NAME, search.CaseStudyDocType),
    )
    for index_name, doc_type in indices:
        index = Index(index_name)
        index.doc_type(doc_type)
        index.analyzer(analyzer('english'))
        index.delete(ignore=404)
        index.create()

    for company in CompanyModel.objects.filter(is_published=True):
        search.company_model_to_doc_type(company).save()
        for case_study in company.supplier_case_studies.all():
            search.case_study_model_to_doc_type(case_study).save()
