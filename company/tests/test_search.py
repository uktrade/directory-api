from unittest.mock import patch, Mock, PropertyMock
import datetime

from freezegun import freeze_time
from freezegun.api import datetime_to_fakedatetime, date_to_fakedate
import pytest

from company import documents, helpers, serializers
from company.tests import factories


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
def test_company_doc_type():
    company = factories.CompanyFactory(
        date_of_creation=datetime.date(2000, 10, 10),
        sectors=['AEROSPACE', 'AIRPORTS']
    )
    case_study = factories.CompanyCaseStudyFactory(company=company)

    logo_mock = PropertyMock(return_value=Mock(url='/media/thing.jpg'))
    
    with patch.object(company, 'logo', new_callable=logo_mock):
        doc = documents.company_model_to_document(company)

    company_data_dict = serializers.CompanySerializer(company).data
    company_parser = helpers.CompanyParser(company_data_dict)

    expected_expertise_products_services = []
    for key, values in company.expertise_products_services.items():
        expected_expertise_products_services += values

    expected = {
        'date_of_creation': date_to_fakedate(company.date_of_creation),
        'description': company.description,
        'employees': company.employees,
        'facebook_url': company.facebook_url,
        'pk': str(company.pk),
        'keywords': company.keywords,
        'linkedin_url': company.linkedin_url,
        'logo': 'http://0.0.0.0:8000/media/thing.jpg',
        'modified': datetime_to_fakedatetime(company.modified),
        'name': company.name,
        'number': company.number,
        'has_description': True,
        'sectors': company.sectors,
        'expertise_industries': company.expertise_industries,
        'expertise_regions': company.expertise_regions,
        'expertise_languages': company.expertise_languages,
        'expertise_countries': company.expertise_countries,
        'expertise_products_services': company.expertise_products_services,
        'expertise_products_services_labels': (
            expected_expertise_products_services
        ),
        'sectors_label': ['Aerospace', 'Airports'],
        'expertise_labels': company_parser.expertise_labels_for_search,
        'slug': company.slug,
        'summary': company.summary,
        'case_study_count': 1,
        'has_single_sector': False,
        'is_showcase_company': False,
        'is_published_find_a_supplier': False,
        'is_published_investment_support_directory': False,
        'company_type': 'COMPANIES_HOUSE',
        'supplier_case_studies': [
            {
                'description': case_study.description,
                'image_one_caption': case_study.image_one_caption,
                'image_three_caption': case_study.image_three_caption,
                'image_two_caption': case_study.image_two_caption,
                'keywords': case_study.keywords,
                'pk': case_study.pk,
                'sector': case_study.sector,
                'short_summary': case_study.short_summary,
                'slug': case_study.slug,
                'testimonial': case_study.testimonial,
                'testimonial_company': case_study.testimonial_company,
                'testimonial_job_title': case_study.testimonial_job_title,
                'testimonial_name': case_study.testimonial_name,
                'title': case_study.title,
                'website': case_study.website,
            }
        ],
        'twitter_url': company.twitter_url,
        'website': company.website,
    }

    assert doc.to_dict() == expected
    assert doc.meta.id == company.pk


@pytest.mark.django_db
def test_company_doc_type_single_sector():
    company = factories.CompanyFactory(
        date_of_creation=datetime.date(2000, 10, 10),
        sectors=['AEROSPACE']
    )

    doc = documents.company_model_to_document(company)

    assert doc.to_dict()['has_single_sector'] is True


@pytest.mark.django_db
def test_company_doc_type_single_sector_local_storage(settings):
    settings.STORAGE_CLASS_NAME = 'local-storage'

    company = factories.CompanyFactory()

    logo_mock = PropertyMock(return_value=Mock(url='/media/thing.jpg'))
    with patch.object(company, 'logo', new_callable=logo_mock):
        doc = documents.company_model_to_document(company)

    assert doc.to_dict()['logo'] == 'http://0.0.0.0:8000/media/thing.jpg'


@pytest.mark.django_db
def test_company_doc_type_single_sector_non_local_storage(settings):
    settings.STORAGE_CLASS_NAME = 'default'

    company = factories.CompanyFactory()

    logo_mock = PropertyMock(return_value=Mock(url='http://media.com/a.jpg'))
    with patch.object(company, 'logo', new_callable=logo_mock):
        doc = documents.company_model_to_document(company)

    assert doc.to_dict()['logo'] == 'http://media.com/a.jpg'
