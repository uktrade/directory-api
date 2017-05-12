import datetime

from freezegun import freeze_time
import pytest

from company import search
from company.tests import factories


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
def test_company_doc_type():
    company = factories.CompanyFactory(
        date_of_creation=datetime.date(2000, 10, 10),
        sectors=['AEROSPACE', 'AIRPORTS']
    )
    case_study = factories.CompanyCaseStudyFactory(company=company)

    doc = search.company_model_to_doc_type(company)

    expected = {
        'date_of_creation': '2000-10-10',
        'description': company.description,
        'employees': company.employees,
        'facebook_url': company.facebook_url,
        'pk': str(company.pk),
        'keywords': company.keywords,
        'linkedin_url': company.linkedin_url,
        'logo': company.logo,
        'modified': '2016-11-23T11:21:10.977518Z',
        'name': company.name,
        'number': company.number,
        'sectors': company.sectors,
        'sectors_label': ['Aerospace', 'Airports'],
        'slug': company.slug,
        'summary': company.summary,
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
