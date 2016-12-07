from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from freezegun import freeze_time

from user.models import User as Supplier
from supplier.tests import VALID_REQUEST_DATA as SUPPLIER_DATA
from company.models import Company
from company.tests import VALID_REQUEST_DATA as COMPANY_DATA


headers = (
    'sso_id,name,mobile_number,company_email,company_email_confirmed,'
    'referrer,is_active,date_joined,company_id,company__name,'
    'company__description,company__employees,company__export_status,'
    'company__keywords,company__logo,company__number,company__revenue,'
    'company__sectors,company__website,company__date_of_creation,'
    'company__is_published'
)


class DownloadCSVTestCase:

    def setUp(self):
        superuser = User.objects.create_superuser(
            suppliername='admin', email='admin@example.com', password='test'
        )
        self.client = Client()
        self.client.force_login(superuser)

        self.freezer = freeze_time("2012-01-14 12:00:00")
        self.freezer.start()

    def tearDown(self):
        self.freezer.stop()

    def test_download_csv(self):
        company = Company.objects.create(**COMPANY_DATA)
        supplier = Supplier.objects.create(company=company, **SUPPLIER_DATA)

        data = {
            'action': 'download_csv',
            '_selected_action': Supplier.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:supplier_supplier_changelist'),
            data,
            follow=True
        )

        row_one = (
            '1,,07505605132,gargoyle@example.com,False,google,True,'
            '2017-03-21 13:12:00+00:00,{pk},Test Company,'
            'Company description,,YES,,,01234567,100000.00,,'
            'http://example.com,2010-10-10,False'
        ).format(pk=supplier.company.pk)

        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == headers
        assert actual[1] == row_one

    def test_download_csv_multiple_suppliers(self):
        company1 = Company.objects.create(**COMPANY_DATA)
        company2 = Company.objects.create(number="01234568")
        supplier_data2 = {
            "sso_id": 2,
            "company_email": "2@example.com"
        }
        supplier_data3 = {
            "sso_id": 3,
            "company_email": "3@example.com",
            "mobile_number": "07505605134"
        }

        supplier_one = Supplier.objects.create(
            company=company1, **SUPPLIER_DATA
        )
        supplier_two = Supplier.objects.create(
            company=company2, **supplier_data2
        )
        supplier_three = Supplier.objects.create(
            company=company2, **supplier_data3
        )

        data = {
            'action': 'download_csv',
            '_selected_action': Supplier.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:supplier_supplier_changelist'),
            data,
            follow=True
        )

        row_one = (
            '3,,07505605134,3@example.com,False,,True,'
            '2012-01-14 12:00:00+00:00,{pk},,,,,,,01234568,,,,,False'
        ).format(pk=supplier_three.company.pk)
        row_two = (
            '2,,,2@example.com,False,,True,2012-01-14 12:00:00+00:00,'
            '{pk},,,,,,,01234568,,,,,False'
        ).format(pk=supplier_two.company.pk)
        row_three = (
            '1,,07505605132,gargoyle@example.com,False,google,True,'
            '2017-03-21 13:12:00+00:00,{pk},Test Company,'
            'Company description,,YES,,,01234567,100000.00,,'
            'http://example.com,2010-10-10,False'
        ).format(pk=supplier_one.company.pk)

        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == headers
        assert actual[1] == row_one
        assert actual[2] == row_two
        assert actual[3] == row_three
