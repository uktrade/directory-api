
def get_published_companies_query_params(request):
    params = request.query_params
    limit = int(params.get('limit', 100))
    minimal_number_of_sectors = int(params.get(
        'minimal_number_of_sectors', 0))
    return limit, minimal_number_of_sectors


def prepare_company_data(company):
    return {
        'name': company.name,
        'number': company.number,
        'sectors': company.sectors,
        'employees': company.employees,
        'keywords': company.keywords,
        'website': company.website,
        'facebook_url': company.facebook_url,
        'twitter_url': company.twitter_url,
        'linkedin_url': company.linkedin_url,
        'company_email': company.email_address,
        'summary': company.summary,
        'description': company.description,
        'is_uk_isd_company': company.is_uk_isd_company,
        'is_published_investment_support_directory':
            company.is_published_investment_support_directory,
        'is_published_find_a_supplier':
            company.is_published_find_a_supplier,
    }


def has_enough_sectors(company, minimal_number_of_sectors):
    return len(company.sectors) >= minimal_number_of_sectors


def get_matching_companies(queryset, limit, minimal_number_of_sectors):
    result = []
    companies = [
        company for company in queryset.all()
        if has_enough_sectors(company, minimal_number_of_sectors)]
    for company in companies[:limit]:
        data = prepare_company_data(company)
        result.append(data)
    return result
