from elasticsearch_dsl import field, DocType

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
    date_of_creation = FormattedDate(date_format='%Y-%m-%d')
    description = field.Text()
    employees = field.Text()
    facebook_url = field.Text()
    pk = field.Integer()
    keywords = field.Text()
    linkedin_url = field.Text()
    logo = field.Text()
    has_single_sector = field.Boolean()
    modified = FormattedDate(date_format='%Y-%m-%dT%H:%M:%S.%fZ')
    name = field.Text()
    number = field.Text()
    sectors = field.Text(multi=True)
    sectors_label = field.Text(multi=True)
    slug = field.Text()
    summary = field.Text()
    twitter_url = field.Text()
    website = field.Text()
    supplier_case_studies = field.Nested(
        properties={
            'pk': field.Integer(),
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
        index = 'companies'


def company_model_to_doc_type(company):
    company_doc_type = CompanyDocType(
        meta={'id': company.pk},
        case_study_count=company.supplier_case_studies.count(),
        date_of_creation=company.date_of_creation,
        description=company.description,
        employees=company.employees,
        facebook_url=company.facebook_url,
        has_single_sector=len(company.sectors) == 1,
        keywords=company.keywords,
        linkedin_url=company.linkedin_url,
        logo=company.logo.url if company.logo else '',
        modified=company.modified,
        name=company.name,
        number=company.number,
        pk=str(company.pk),
        sectors=company.sectors,
        sectors_label=[helpers.get_sector_label(v) for v in company.sectors],
        slug=company.slug,
        summary=company.summary,
        twitter_url=company.twitter_url,
        website=company.website,
    )
    for case_study in company.supplier_case_studies.all():
        company_doc_type.supplier_case_studies.append({
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
        })
    return company_doc_type
