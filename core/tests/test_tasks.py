from unittest import mock
from dataservices import helpers, tasks


@mock.patch.object(tasks, 'pre_populate_comtrade_data_item')
@mock.patch.object(helpers.MADB, 'get_madb_country_list')
def test_pre_populate_comtrade_data(mock_get_country_list, mock_pre_populate_comtrade_data_item):

    mock_get_country_list.return_value = [
        ('Australia', 'Australia'),
    ]
    tasks.pre_populate_comtrade_data()
    assert mock_pre_populate_comtrade_data_item.call_count == 1
    assert mock_pre_populate_comtrade_data_item.call_args == mock.call(
        commodity_code='2208.50.00.57', country='Australia'
    )


@mock.patch.object(helpers, 'get_historical_import_data')
@mock.patch.object(helpers, 'get_last_year_import_data')
def test_pre_populate_comtrade_data_item(mock_get_last_year_import_data, mock_get_historical_import_data):

    tasks.pre_populate_comtrade_data_item(commodity_code='123', country='UK')
    assert mock_get_last_year_import_data.call_count == 1
    assert mock_get_last_year_import_data.call_args == mock.call(commodity_code='123', country='UK')

    assert mock_get_historical_import_data.call_count == 1
    assert mock_get_historical_import_data.call_args == mock.call(commodity_code='123', country='UK')
