from urllib.parse import urljoin

from elasticsearch_dsl import field, DocType

from django.conf import settings

from company import helpers


class FormattedDate(field.Date):
    def __init__(self, date_format, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date_format = date_format

    def _deserialize(self, *args, **kwargs):
        date = super()._deserialize(*args, **kwargs)
        if date:
            return date.strftime(self.date_format)

    def to_dict(self, *args, **kwargs):
        value = super().to_dict(*args, **kwargs)
        del value['date_format']
        return value


class CompanyDocType(DocType):
    case_study_count = field.Integer()
    date_of_creation = FormattedDate(date_format='%Y-%m-%d', index='no')
    description = field.Text()
    has_description = field.Boolean()
    employees = field.Text(index='no')
    facebook_url = field.Text(index='no')
    pk = field.Integer(index='no')
    keywords = field.Text()
    linkedin_url = field.Text(index='no')
    logo = field.Text(index='no')
    has_single_sector = field.Boolean()
    modified = FormattedDate(date_format='%Y-%m-%dT%H:%M:%S.%fZ', index='no')
    name = field.Text()
    number = field.Text()
    sectors = field.Text(multi=True)
    sectors_label = field.Text(multi=True)
    slug = field.Text()
    summary = field.Text()
    twitter_url = field.Text(index='no')
    website = field.Text()
    campaign_tag = field.Text()
    supplier_case_studies = field.Nested(
        properties={
            'pk': field.Integer(index='no'),
            'title': field.Text(),
            'short_summary': field.Text(),
            'description': field.Text(),
            'sector': field.Text(),
            'keywords': field.Text(),
            'image_one_caption': field.Text(),
            'image_two_caption': field.Text(),
            'image_three_caption': field.Text(),
            'testimonial': field.Text(),
            'slug': field.Text(),
        }
    )

    class Meta:
        index = settings.ELASTICSEARCH_COMPANY_INDEX


class CaseStudyDocType(DocType):
    pk = field.Integer(index='no')
    title = field.Text()
    short_summary = field.Text()
    description = field.Text()
    sector = field.Text()
    keywords = field.Text()
    image = field.Text(index='no')
    company_number = field.Text(index='no')
    image_one_caption = field.Text()
    image_two_caption = field.Text()
    image_three_caption = field.Text()
    testimonial = field.Text()
    slug = field.Text(index='no')
    campaign_tag = field.Text()

    class Meta:
        index = settings.ELASTICSEARCH_CASE_STUDY_INDEX


def get_absolute_url(url):
    if settings.STORAGE_CLASS_NAME == 'local-storage':
        return urljoin(settings.LOCAL_STORAGE_DOMAIN, url)
    return url


def company_model_to_doc_type(company):
    # getattr is used on the company to allow this functionton be used in
    # migrations (historic models wont have all the fields listed below).
    company_fields = {
        'date_of_creation',
        'description',
        'employees',
        'facebook_url',
        'keywords',
        'linkedin_url',
        'modified',
        'name',
        'number',
        'sectors',
        'slug',
        'summary',
        'twitter_url',
        'website',
        'campaign_tag',
    }
    case_study_fields = {
        'description',
        'image_one_caption',
        'image_three_caption',
        'image_two_caption',
        'keywords',
        'pk',
        'sector',
        'short_summary',
        'slug',
        'testimonial',
        'testimonial_company',
        'testimonial_job_title',
        'testimonial_name',
        'title',
        'website',
    }
    has_description = getattr(company, 'description', '') != ''
    company_doc_type = CompanyDocType(
        meta={'id': company.pk},
        pk=str(company.pk),
        case_study_count=company.supplier_case_studies.count(),
        has_single_sector=len(company.sectors) == 1,
        has_description=has_description,
        logo=get_absolute_url(company.logo.url if company.logo else ''),
        sectors_label=[helpers.get_sector_label(v) for v in company.sectors],
        **{key: getattr(company, key, '') for key in company_fields},
    )
    for case_study in company.supplier_case_studies.all():
        company_doc_type.supplier_case_studies.append({
            key: getattr(case_study, key, '') for key in case_study_fields
        })
    return company_doc_type


def case_study_model_to_doc_type(case_study):
    # getattr is used on the case study to allow this functionton be used in
    # migrations (historic models wont have all the fields listed below).
    fields = {
        'description',
        'image_one_caption',
        'image_three_caption',
        'image_two_caption',
        'keywords',
        'pk',
        'sector',
        'short_summary',
        'slug',
        'title',
        'campaign_tag',
    }
    return CaseStudyDocType(
        meta={'id': case_study.pk},
        image=get_absolute_url(
            case_study.image_one.url if case_study.image_one else '',
        ),
        company_number=case_study.company.number,
        **{key: getattr(case_study, key, '') for key in fields},
    )
