import requests
import json
import pandas
from airtable import Airtable

from django.core.cache import cache
from dataservices import models, serializers

from datetime import datetime


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
            historical_year_start = datetime.today().year-2
            historical_year_end = historical_year_start-1
            year_import = comdata_df[comdata_df.period == historical_year_start]
            last_year_import = comdata_df[comdata_df.period == historical_year_end]['TradeValue'].iloc[0]

            return {
                    'year': str(year_import.iloc[0]['period']),
                    'trade_value': str(year_import.iloc[0]['TradeValue']),
                    'country_name': year_import.iloc[0]['rtTitle'],
                    'year_on_year_change': str(round(last_year_import/year_import.iloc[0]['TradeValue'], 3)),
            }

    def get_historical_import_value_partner_country(self, no_years=3):
        comdata = requests.get(self.get_url())
        comdata_df = pandas.DataFrame.from_dict(comdata.json()['dataset'])
        if not comdata_df.empty:
            historical_trade_values = {}
            reporting_year_df = comdata_df.sort_values(by=['period'], ascending=False).head(no_years)

            for index, row in reporting_year_df.iterrows():
                historical_trade_values[row['period']] = str(row['TradeValue'])
            return historical_trade_values

    def get_historical_import_value_world(self, no_years=3):
        historical_trade_values = {}

        for y in range(1, no_years+1):
            reporting_year = datetime.today().year-(y+1)
            url_options = f'&r=All&p={self.partner_country_id}&cc={self.product_code}&ps={reporting_year}'
            world_data = requests.get(self.url + url_options)
            world_data_df = pandas.DataFrame.from_dict(world_data.json()['dataset'])
            if not world_data_df.empty:
                str(world_data_df['TradeValue'].sum())
                historical_trade_values[reporting_year] = str(
                    world_data_df['TradeValue'].sum()
                )
        return historical_trade_values

    def get_all_historical_import_value(self, no_years=3):
        historical_data = {}
        country_data = self.get_historical_import_value_partner_country(no_years)
        world_data = self.get_historical_import_value_world(no_years)

        historical_data['historical_trade_value_partner'] = country_data
        historical_data['historical_trade_value_all'] = world_data
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


class TTLCache:

    def __init__(self, default_cache_max_age=60*60*24):
        self.default_max_age = default_cache_max_age

    def get_cache_value(self, key):
        return cache.get(key, default=None)

    def set_cache_value(self, key, value):
        cache.set(key, value, self.default_max_age)

    def __call__(self, func):
        def inner(*args, **kwargs):
            cache_key = json.dumps([func.__name__, kwargs, args], sort_keys=True, separators=(',', ':'))
            cached_value = self.get_cache_value(cache_key)
            if not cached_value:
                cached_value = func(*args, **kwargs)
                self.set_cache_value(cache_key, cached_value)
            return cached_value
        return inner


@TTLCache()
def get_ease_of_business_index(country_code):
    try:
        instance = models.EaseOfDoingBusiness.objects.get(country_code=country_code)
        serializer = serializers.EaseOfDoingBusinessSerializer(instance)
        return serializer.data
    except models.EaseOfDoingBusiness.DoesNotExist:
        return None


@TTLCache()
def get_corruption_perception_index(country_code):
    try:
        instance = models.CorruptionPerceptionsIndex.objects.get(country_code=country_code)
        serializer = serializers.CorruptionPerceptionsIndexSerializer(instance)
        return serializer.data
    except models.CorruptionPerceptionsIndex.DoesNotExist:
        return None


@TTLCache()
def get_last_year_import_data(country, commodity_code):
    comtrade = ComTradeData(commodity_code=commodity_code, reporting_area=country)
    last_year_data = comtrade.get_last_year_import_data()
    return last_year_data


@TTLCache()
def get_historical_import_data(country, commodity_code):
    comtrade = ComTradeData(commodity_code=commodity_code, reporting_area=country)
    historical_data = comtrade.get_all_historical_import_value()
    return historical_data
