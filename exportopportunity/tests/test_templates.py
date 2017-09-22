import pytest

from django.template.loader import render_to_string

from exportopportunity.tests import factories


@pytest.mark.django_db
def test_opportunity_submitted_email():
    instance = factories.ExportOpportunityFactory(
        business_model=['distribution'],
        target_sectors=['retail'],
        products=['PREMIUM'],
        order_size='1-1000',
        order_deadline='1-3 MONTHS',
        full_name='jim Example',
        job_title='Exampler',
        email_address='jim@example.com',
        company_name='Jimmer corp',
        company_website='http://www.example.com',
        phone_number='07506076945',
        contact_preference=['PHONE'],
        campaign='food-is-great',
        country='france',
        additional_requirements='Bring me a shrubbery',
        business_model_other='shhh!',
        target_sectors_other='calm yourself',
        products_other='follow your dreams',
    )
    context = {'instance': instance}
    html = render_to_string('email/opportunity-submitted.txt', context)

    assert html == (
        'Hello,\n\n'
        'An international buyer has submitted the following '
        'export opportunity lead via trade.great.gov.uk:\n\n'
        'Business model: distribution shhh!\n'
        'Target sectors: retail calm yourself\n'
        'Products: PREMIUM follow your dreams\n'
        'Order size: 1-1000\n'
        'Order Deadline: 1-3 MONTHS\n'
        'Additional_requirements: Bring me a shrubbery\n\n'
        'Contact details:\n\n'
        'Name: jim Example\n'
        'Job title: Exampler\n'
        'Email: jim@example.com\n'
        'Company: Jimmer corp\n'
        'Website: http://www.example.com\n'
        'Phone number: 07506076945\n'
        'Contact preference: PHONE\n\n'
        'Campaign: food-is-great\n'
        'Country: france\n\n'
        'kind regards,\n\n'
        'Your trade.great.gov.uk friends\n'
    )
