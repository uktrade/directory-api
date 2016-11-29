from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser

from freezegun import freeze_time

from user.models import User
from user.tests import VALID_REQUEST_DATA as USER_DATA
from company.models import Company
from company.tests import VALID_REQUEST_DATA as COMPANY_DATA


headers = (
    'sso_id,name,mobile_number,company_email,company_email_confirmed,r'
    'eferrer,is_active,date_joined,terms_agreed,company_id,company__na'
    'me,company__description,company__employees,company__export_status'
    ',company__keywords,company__logo,company__number,company__revenue'
    ',company__sectors,company__website,company__date_of_creation,comp'
    'any__is_published'
)


class DownloadCSVTestCase:

    def setUp(self):
        superuser = DjangoUser.objects.create_superuser(
            username='admin', email='admin@example.com', password='test'
        )
        self.client = Client()
        self.client.force_login(superuser)

        self.freezer = freeze_time("2012-01-14 12:00:00")
        self.freezer.start()

    def tearDown(self):
        self.freezer.stop()

    def test_download_csv(self):
        company = Company.objects.create(**COMPANY_DATA)
        user = User.objects.create(company=company, **USER_DATA)

        data = {
            'action': 'download_csv',
            '_selected_action': User.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:user_user_changelist'),
            data,
            follow=True
        )

        row_one = (
            '1,,07505605132,gargoyle@example.com,False,google,True,'
            '2017-03-21 13:12:00+00:00,True,{pk},Test Company,'
            'Company description,,YES,,,01234567,100000.00,,'
            'http://example.com,2010-10-10,False'
        ).format(pk=user.company.pk)

        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == headers
        assert actual[1] == row_one

    def test_download_csv_multiple_users(self):
        company1 = Company.objects.create(**COMPANY_DATA)
        company2 = Company.objects.create(number="01234568")
        user_data2 = {"sso_id": 2, "company_email": "2@example.com"}
        user_data3 = {"sso_id": 3, "company_email": "3@example.com",
                      "mobile_number": "07505605134"}

        user_one = User.objects.create(company=company1, **USER_DATA)
        user_two = User.objects.create(company=company2, **user_data2)
        user_three = User.objects.create(company=company2, **user_data3)

        data = {
            'action': 'download_csv',
            '_selected_action': User.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:user_user_changelist'),
            data,
            follow=True
        )

        row_one = (
            '3,,07505605134,3@example.com,False,,True,'
            '2012-01-14 12:00:00+00:00,False,{pk},,,,,,,01234568,,,,,False'
        ).format(pk=user_three.company.pk)
        row_two = (
            '2,,,2@example.com,False,,True,2012-01-14 12:00:00+00:00,False,'
            '{pk},,,,,,,01234568,,,,,False'
        ).format(pk=user_two.company.pk)
        row_three = (
            '1,,07505605132,gargoyle@example.com,False,google,True,'
            '2017-03-21 13:12:00+00:00,True,{pk},Test Company,'
            'Company description,,YES,,,01234567,100000.00,,'
            'http://example.com,2010-10-10,False'
        ).format(pk=user_one.company.pk)

        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == headers
        assert actual[1] == row_one
        assert actual[2] == row_two
        assert actual[3] == row_three
