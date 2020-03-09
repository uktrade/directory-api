import requests
import json
import pandas as pd
import datetime


class ComTradeData():
    url = (
        'https://comtrade.un.org/api/get?type=C&freq=A&px=HS&rg=1'
    )

    def __init__(self, commodity_code, reporting_area, partner_country='United Kingdom'):
        pd.set_option('mode.chained_assignment', None)
        self.product_code = self.get_product_code(commodity_code)
        self.reporting_area_id = self.get_comtrade_company_id(reporting_area)
        self.partner_country_id = self.get_comtrade_company_id(partner_country)

    def get_comtrade_company_id(self, country_name):
        with open('dataservices/resources/reporterAreas.json', 'r') as f:
            json1_str = f.read()
            counties_data = pd.DataFrame(json.loads(json1_str)['results'])
            return counties_data[counties_data['text'] == country_name]['id'].iloc[0]

    def get_url(self):
        url_options = f'&r={self.reporting_area_id}&p={self.partner_country_id}&cc={self.product_code}&ps=All'
        return self.url + url_options

    def get_product_code(self, commodity_code):
        commodity_list = commodity_code.split('.')[0:2]
        return ''.join(commodity_list)

    def get_last_year_import_data(self):

        comdata = requests.get(self.get_url())
        comdata_df = pd.DataFrame.from_dict(comdata.json()['dataset'])

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
        comdata_df = pd.DataFrame.from_dict(comdata.json()['dataset'])

        historical_trade_values = {'historical_trade_value_partner': {}}

        reporting_year_df = comdata_df.sort_values(by=['yr'], ascending=False).head(no_years)

        for index, row in reporting_year_df.iterrows():
            historical_trade_values['historical_trade_value_partner'][row['yr']] = row['TradeValue']
        return historical_trade_values

    def get_historical_import_value_world(self, no_years=3):
        historical_trade_values = {'historical_trade_value_all': {}}

        for y in range(1, no_years+1):
            reporting_year = datetime.datetime.today().year-(y+1)
            url_options = f'&r=All&p={self.partner_country_id}&cc={self.product_code}&ps={reporting_year}'
            world_data = requests.get(self.url + url_options)
            world_data_df = pd.DataFrame.from_dict(world_data.json()['dataset'])
            world_data_df['TradeValue'].sum()
            historical_trade_values['historical_trade_value_all'][reporting_year] = world_data_df['TradeValue'].sum()
        return historical_trade_values
