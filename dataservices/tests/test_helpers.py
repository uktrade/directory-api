import re
from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import patch
import zlib

import boto3
import pytest
from botocore.paginate import Paginator
from botocore.stub import Stubber
from django.conf import settings
from django.test import override_settings
from freezegun import freeze_time

from dataservices import helpers, models
from dataservices.management.commands import helpers as dmch
from dataservices.tests import factories, utils


@pytest.fixture()
def comtrade_data():
    return {
        "dataset": [
            {
                "period": 2018,
                "rtTitle": "Australia",
                "ptTitle": "United Kingdom",
                "TradeValue": 200,
            },
            {
                "period": 2017,
                "rtTitle": "Australia",
                "ptTitle": "United Kingdom",
                "TradeValue": 100,
            },
            {
                "period": 2016,
                "rtTitle": "Italy",
                "ptTitle": "United Kingdom",
                "TradeValue": 50,
            },
        ]
    }


@pytest.fixture()
def comtrade_data_with_a_year_data():
    return {
        "dataset": [
            {
                "period": 2018,
                "rtTitle": "Australia",
                "ptTitle": "United Kingdom",
                "TradeValue": 200,
            },
        ]
    }


@pytest.fixture()
def comtrade_data_with_various_year_data():
    return {
        "dataset": [
            {
                "period": 2018,
                "rtTitle": "Australia",
                "ptTitle": "United Kingdom",
                "TradeValue": 200,
            },
            {
                "period": 2013,
                "rtTitle": "Australia",
                "ptTitle": "United Kingdom",
                "TradeValue": 200,
            },
        ]
    }


@pytest.fixture()
def comtrade_data_with_various_data_request_mock(comtrade_data_with_various_year_data, requests_mocker):
    return requests_mocker.get(
        re.compile('https://comtrade\.un\.org/.*'), json=comtrade_data_with_various_year_data  # noqa
    )


@pytest.fixture()
def comtrade_data_with_a_year_data_request_mock(comtrade_data_with_a_year_data, requests_mocker):
    return requests_mocker.get(re.compile('https://comtrade\.un\.org/.*'), json=comtrade_data_with_a_year_data)  # noqa


@pytest.mark.django_db
def test_get_comtrade_data_by_country():
    commodity_code = '123456'
    aus = models.Country.objects.create(name="Australia", iso3="AUS", iso2='AU', iso1=36)
    bel = models.Country.objects.create(name="Belgium", iso3="BEL", iso2='BE', iso1=56)

    report = {
        'uk_or_world': 'WLD',
        'commodity_code': commodity_code,
        'trade_value': '222222',
        'year': 2019,
    }
    wld_report = report.copy()
    uk_report = report.copy()
    uk_report.update(
        {
            'uk_or_world': 'GBR',
            'trade_value': '111111',
        }
    )

    wrong_product = report.copy()
    wrong_product.update({'commodity_code': '234567'})

    models.ComtradeReport.objects.create(country=aus, **wld_report)
    models.ComtradeReport.objects.create(country=aus, **uk_report)
    models.ComtradeReport.objects.create(country=aus, **wrong_product)
    models.ComtradeReport.objects.create(country=bel, **wld_report)
    models.ComtradeReport.objects.create(country=bel, **uk_report)
    models.ComtradeReport.objects.create(country=bel, **wrong_product)

    # Get one country
    data = helpers.get_comtrade_data_by_country(commodity_code, ['AU'])
    assert len(data) == 1
    country_data = data['AU']
    assert len(country_data) == 2
    data_order = [wld_report, uk_report] if country_data[0].get('uk_or_world') == 'WLD' else [uk_report, wld_report]
    assert utils.deep_compare(country_data[0], data_order[0])
    assert utils.deep_compare(country_data[1], data_order[1])

    # Get two countries
    data = helpers.get_comtrade_data_by_country(commodity_code, ['AU', 'BE'])
    assert len(data) == 2
    country_data = data['BE']
    data_order = [wld_report, uk_report] if country_data[0].get('uk_or_world') == 'WLD' else [uk_report, wld_report]
    assert utils.deep_compare(country_data[0], data_order[0])
    assert utils.deep_compare(country_data[1], data_order[1])


@pytest.mark.django_db
def test_get_cia_factbook_by_country_all_data():
    cia_factbook_data_test_data = factories.CIAFactBookFactory()
    cia_factbook_data = helpers.get_cia_factbook_data('United Kingdom')
    assert cia_factbook_data == cia_factbook_data_test_data.factbook_data


@pytest.mark.django_db
def test_get_cia_factbook_country_not_found():
    cia_factbook_data = helpers.get_cia_factbook_data('xyz')
    assert cia_factbook_data == {}


@pytest.mark.django_db
def test_get_cia_factbook_by_keys():
    factories.CIAFactBookFactory()
    cia_factbook_data = helpers.get_cia_factbook_data(country_name='United Kingdom', data_keys=['capital', 'currency'])

    assert cia_factbook_data == {'capital': 'London', 'currency': 'GBP'}


@pytest.mark.django_db
def test_get_cia_factbook_by_keys_some_bad_Keys():
    factories.CIAFactBookFactory()
    cia_factbook_data = helpers.get_cia_factbook_data(country_name='United Kingdom', data_keys=['capital', 'xyz'])
    assert cia_factbook_data == {'capital': 'London'}


@pytest.mark.django_db
def test_get_internet_usage(internet_usage_data):
    data = helpers.get_internet_usage(country='United Kingdom')
    assert data == {'internet_usage': {'value': '90.97', 'year': 2020}}


@pytest.mark.django_db
def test_get_internet_usage_with_no_country():
    data = helpers.get_internet_usage(country='Random Country')
    assert data == {}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "o1,o2,result",
    [
        ({'a': 'a', 'b': 'b'}, {'d': 'd', 'b': 'b2'}, {'a': 'a', 'd': 'd', 'b': 'b2'}),
        ({'a': 'a', 'b': {'c': 'c'}}, {'d': 'd', 'b': {'e': 'e'}}, {'a': 'a', 'd': 'd', 'b': {'c': 'c', 'e': 'e'}}),
        ({'a': 'a', 'b': 'b'}, {'d': 'd', 'b': {'c': 'c'}}, {'a': 'a', 'd': 'd', 'b': {'c': 'c'}}),
        ({'a': 'a', 'b': {'c': 'c'}}, {'d': 'd', 'b': 'b2'}, {'a': 'a', 'd': 'd', 'b': 'b2'}),
    ],
)
def test_deep_extend(o1, o2, result):
    assert helpers.deep_extend(o1, o2) == result


@pytest.mark.django_db
@mock.patch('dataservices.management.commands.helpers.notifications_client')
def test_notify_error_message(mock_notify):
    dmch.send_ingest_error_notify_email('TestView', Exception('lol'))
    mock_notify.call_args = mock.call(
        email_address='a@b.com',
        template_id=settings.GOVNOTIFY_ERROR_MESSAGE_TEMPLATE_ID,
        personalisation={
            'area_of_error': 'view name',
            'error_type': 'type error details',
            'error_details': 'all error details',
        },
    )
    assert mock_notify.call_count == 1


@freeze_time('2023-09-13T15:21:10')
@pytest.mark.django_db
@mock.patch('dataservices.management.commands.helpers.notifications_client')
@pytest.mark.parametrize(
    "last_release, notification_sent, result",
    [
        (datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), None, 1),
        (
            datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%dT%H:%M:%S'),
            1,
        ),
        (
            datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            (datetime.now() + timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%S'),
            0,
        ),
    ],
)
def test_send_review_request_message(mock_notify, last_release, notification_sent, result):
    data = {'source': {'last_release': last_release}}
    data['review_process'] = {} if notification_sent is None else {'notification_sent': notification_sent}
    factories.MetadataFactory(view_name='TestView', data=data)
    dmch.send_review_request_message('TestView')
    mock_notify.call_args = mock.call(
        email_address='a@b.com',
        template_id=settings.GOVNOTIFY_GREAT_MARKETGUIDES_REVIEW_REQUEST_TEMPLATE_ID,
        personalisation={
            'view_name': 'view_name',
            'review_url': 'https://great.staging.uktrade.digital/markets/',
            'release_date': 'dd/mm/YYYY',
        },
    )
    assert mock_notify.call_count == result


@pytest.mark.django_db
@pytest.mark.parametrize(
    'statista_vertical_name, expected_vertical_name',
    [
        ('Technology & Smart Cities', 'Technology and Smart Cities'),
        ('Pharmaceuticals and Biotech', 'Pharmaceuticals and biotechnology'),
        ('Manufacture of medical and dental instruments and supplies', 'Medical devices and equipment'),
        ('Automovie', 'Automotive'),
        ('Food and Drink', 'Food and Drink'),
        ('Space', 'Space'),
    ],
)
def test_align_vertical_names(statista_vertical_name, expected_vertical_name):
    assert dmch.align_vertical_names(statista_vertical_name) == expected_vertical_name


@pytest.mark.django_db
@patch.object(Paginator, 'paginate')
def test_get_s3_paginator(mock_paginate, get_s3_data_transfer_data):
    client = boto3.client('s3')
    stubber = Stubber(client)
    mock_paginate.return_value = get_s3_data_transfer_data
    prefix = settings.POSTCODE_FROM_S3_PREFIX
    stubber.activate()

    with mock.patch('boto3.client', mock.MagicMock(return_value=client)):
        response = dmch.get_s3_paginator(prefix=prefix)

    assert response == get_s3_data_transfer_data


@pytest.mark.django_db
def test_get_s3_file(get_s3_file_data):
    client = boto3.client('s3')
    stubber = Stubber(client)
    key = 'testfile_jsonl.zx'
    stubber.add_response(
        method='get_object',
        service_response=get_s3_file_data,
        expected_params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME_DATA_SERVICES, 'Key': key},
    )
    stubber.activate()
    with mock.patch('boto3.client', mock.MagicMock(return_value=client)):
        response = dmch.get_s3_file(key=key)

    assert response == get_s3_file_data


@pytest.mark.django_db
@mock.patch.object(zlib, 'decompressobj')
def test_unzip_s3_gzip_file_eof(mock_decompressobj):
    mock_decompressobj.flush.return_value = 'Not Null'
    file = dmch.unzip_s3_gzip_file(file_body=b'', max_bytes=(32 + zlib.MAX_WBITS))
    val = next(file)
    assert val is not None


# @pytest.mark.django_db
# def test_unzip_s3_gzip_file_eof():
#     body_json = {
#         'pcd': 'N17 9SJ',
#         'rgn': 'London',
#     }
#     body_encoded = json.dumps(body_json).encode()
#     gzipped_body = gzip.compress(body_encoded)
#     body = StreamingBody(io.BytesIO(gzipped_body), len(gzipped_body))
#     file = dmch.unzip_s3_gzip_file(file_body=body, max_bytes=(32 + zlib.MAX_WBITS))
#     next(file)
#     with pytest.raises(StopIteration):
#         next(file)


@pytest.mark.django_db
@override_settings(DATABASE_URL='postgresql://')
@mock.patch('dataservices.management.commands.helpers.ingest_data')
def test_save_postcode_data(mock_ingest_data, postcode_data):
    dmch.save_postcode_data(data=postcode_data)
    assert mock_ingest_data.call_count == 1
