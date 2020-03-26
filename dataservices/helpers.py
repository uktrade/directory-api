import requests
import json
import pandas
import datetime
from airtable import Airtable


class ComTradeData:
    url = 'https://comtrade.un.org/api/get?type=C&freq=A&px=HS&rg=1'

    def __init__(self, commodity_code, reporting_area, partner_country='United Kingdom'):
        pandas.set_option('mode.chained_assignment', None)
        self.product_code = self.get_product_code(commodity_code)
        self.reporting_area_id = self.get_comtrade_company_id(reporting_area)
        self.partner_country_id = self.get_comtrade_company_id(partner_country)

    def get_comtrade_company_id(self, country_name):
        with open('dataservices/resources/reporterAreas.json', 'r') as f:
            json1_str = f.read()
            counties_data = pandas.DataFrame(json.loads(json1_str)['results'])
            if not counties_data[counties_data['text'] == country_name]['id'].empty:
                return counties_data[counties_data['text'] == country_name]['id'].iloc[0]
            else:
                return ''

    def get_url(self):
        url_options = f'&r={self.reporting_area_id}&p={self.partner_country_id}&cc={self.product_code}&ps=All'
        return self.url + url_options

    def get_product_code(self, commodity_code):
        commodity_list = commodity_code.split('.')[0:2]
        return ''.join(commodity_list)

    def get_last_year_import_data(self):

        comdata = requests.get(self.get_url())
        comdata_df = pandas.DataFrame.from_dict(comdata.json()['dataset'])
        if not comdata_df.empty:
            # Get Last two years data
            last_year = datetime.datetime.today().year-2
            previous_year = last_year-1
            year_import = comdata_df[comdata_df.period == last_year]
            last_year_import = comdata_df[comdata_df.period == previous_year]['TradeValue'].iloc[0]

            return {
                'import_value':
                {
                    'year': year_import.iloc[0]['period'],
                    'trade_value': year_import.iloc[0]['TradeValue'],
                    'country_name': year_import.iloc[0]['rtTitle'],
                    'year_on_year_change': round(last_year_import/year_import.iloc[0]['TradeValue'], 3),
                }
            }

    def get_historical_import_value_partner_country(self, no_years=3):
        comdata = requests.get(self.get_url())
        comdata_df = pandas.DataFrame.from_dict(comdata.json()['dataset'])
        if not comdata_df.empty:
            historical_trade_values = {}
            reporting_year_df = comdata_df.sort_values(by=['period'], ascending=False).head(no_years)

            for index, row in reporting_year_df.iterrows():
                historical_trade_values[row['period']] = row['TradeValue']
            return historical_trade_values

    def get_historical_import_value_world(self, no_years=3):
        historical_trade_values = {}

        for y in range(1, no_years+1):
            reporting_year = datetime.datetime.today().year-(y+1)
            url_options = f'&r=All&p={self.partner_country_id}&cc={self.product_code}&ps={reporting_year}'
            world_data = requests.get(self.url + url_options)
            world_data_df = pandas.DataFrame.from_dict(world_data.json()['dataset'])
            if not world_data_df.empty:
                world_data_df['TradeValue'].sum()
                historical_trade_values[reporting_year] = (
                    world_data_df['TradeValue'].sum()
                )
        return historical_trade_values

    def get_all_historical_import_value(self, no_years=3):
        historical_data = {'historical_import_data': {}}
        country_data = self.get_historical_import_value_partner_country(no_years)
        world_data = self.get_historical_import_value_world(no_years)

        historical_data['historical_import_data']['historical_trade_value_partner'] = country_data
        historical_data['historical_import_data']['historical_trade_value_all'] = world_data
        return historical_data


class MADB:

    def get_madb_country_list(self):
        airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
        airtable_data = airtable.get_all(view='Grid view')
        country_list = [c['country'] for c in [f['fields'] for f in airtable_data]]
        return list(zip(country_list, country_list))

    def get_madb_commodity_list(self):
        airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
        commodity_name_set = set()
        for row in airtable.get_all(view='Grid view'):
            commodity_code = row['fields']['commodity_code']
            commodity_name = row['fields']['commodity_name']
            commodity_name_code = f'{commodity_name} - {commodity_code}'
            commodity_name_set.add((commodity_code, commodity_name_code))
        return commodity_name_set

    def get_rules_and_regulations(self, country):
        airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
        rules = airtable.search('country', country)
        if rules:
            return rules[0]['fields']
