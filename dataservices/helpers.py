from itertools import chain
from datetime import datetime

import json
import math
import pandas
import requests

from django.core.cache import cache
from dataservices import models, serializers

COUNTRIES_MAP = {
    'United States': 'USA',
}

class ComTradeData:
    url = 'https://comtrade.un.org/api/get?type=C&freq=A&px=HS'

    def __init__(self, commodity_code, reporting_area, partner_country='United Kingdom'):
        pandas.set_option('mode.chained_assignment', None)
        self.product_code = self.get_product_code(commodity_code)
        self.reporting_area_id = self.get_comtrade_company_id(COUNTRIES_MAP.get(reporting_area, reporting_area))
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
        url_options = f'&r={self.reporting_area_id}&p={self.partner_country_id}&cc={self.product_code}&ps=All&rg=1'
        return self.url + url_options

    def get_product_code(self, commodity_code):
        commodity_list = commodity_code.split('.')[0:2]
        return ''.join(commodity_list)

    def get_last_year_import_data(self):

        comdata = requests.get(self.get_url())
        if 'dataset' in comdata.json() and comdata.json()['dataset']:
            comdata_df = pandas.DataFrame.from_dict(comdata.json()['dataset']).sort_values(by='period', ascending=False)

            if not comdata_df.empty:
                # Get Last two years data
                year_import = comdata_df[comdata_df.period == comdata_df.period.max()]
                year_on_year_change = None
                # check if data available for more than one year
                if len(comdata_df.index) > 1:

                    try:
                        last_year_import = comdata_df[comdata_df.period == comdata_df.period.max()-1]['TradeValue'].iloc[0]
                        year_on_year_change = str(round(last_year_import / year_import.iloc[0]['TradeValue'], 3))
                    except IndexError:
                        pass

                return {
                    'year': str(year_import.iloc[0]['period']),
                    'trade_value': str(year_import.iloc[0]['TradeValue']),
                    'country_name': year_import.iloc[0]['rtTitle'],
                    'year_on_year_change': year_on_year_change,
                }

    def get_last_year_import_data_from_uk(self):

        url = self.url + f'&r={self.reporting_area_id}&p={self.partner_country_id}&cc={self.product_code}&ps=All&rg=2'
        comdata = requests.get(url)
        
        if 'dataset' in comdata.json() and comdata.json()['dataset']:
            comdata_df = pandas.DataFrame.from_dict(comdata.json()['dataset']).sort_values(by='period', ascending=False)
            if not comdata_df.empty:
                # Get Last two years data
                year_import = comdata_df[comdata_df.period == comdata_df.period.max()]
                # check if data available for more than one year
                year_on_year_change = None
                if len(comdata_df.index) > 1:
                    try:
                        last_year_import = comdata_df[comdata_df.period == comdata_df.period.max()-1]['TradeValue'].iloc[0]
                        year_on_year_change = str(round(last_year_import/year_import.iloc[0]['TradeValue'], 3))
                    except IndexError:
                        pass
                return {
                        'year': str(year_import.iloc[0]['period']),
                        'trade_value': str(year_import.iloc[0]['TradeValue']),
                        'country_name': year_import.iloc[0]['rtTitle'],
                        'year_on_year_change': year_on_year_change,
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


class PopulationData:
    un_male_pop_data = None
    un_female_pop_data = None
    un_rural_pop = None
    un_urban_pop = None
    year = 0
    un_to_dit_country_map = {
        'United States of America': 'United States',
        'Bolivia (Plurinational State of)': 'Bolivia',
        'Brunei Darussalam': 'Brunei',
        'Democratic Republic of the Congo': 'Congo (Democratic Republic)',
        'Iran (Islamic Republic of)': 'Iran',
        'Republic of Moldova': 'Moldova',
        'Myanmar': 'Myanmar (Burma)',
        'Russian Federation': 'Russia',
        'Saint Lucia': 'St Lucia',
        'Saint Vincent and the Grenadines': 'St Vincent',
        'Syrian Arab Republic': 'Syria',
        'United Republic of Tanzania': 'Tanzania',
        'Bahamas': 'The Bahamas',
        'Gambia': 'The Gambia',
        'Venezuela (Bolivarian Republic of)': 'Venezuela',
    }

    def __init__(self):
        pandas.set_option('mode.chained_assignment', None)
        self.un_male_pop_data = pandas.read_csv('dataservices/resources/world_population_medium_male.csv')
        self.un_female_pop_data = pandas.read_csv('dataservices/resources/world_population_medium_female.csv')
        self.un_rural_pop = pandas.read_csv('dataservices/resources/rural_population_annual.csv')
        self.un_urban_pop = pandas.read_csv('dataservices/resources/urban_population_annual.csv')
        self.year = datetime.today().year

        # Lets make the counties columns consistent with out own source
        self.un_male_pop_data = self.map_country_data(self.un_male_pop_data)
        self.un_female_pop_data = self.map_country_data(self.un_female_pop_data)
        self.un_rural_pop = self.map_country_data(self.un_rural_pop)
        self.un_urban_pop = self.map_country_data(self.un_urban_pop)

    def map_country_data(self, country_data):
        # This function is used to map the DS to match our naming convention for countries
        country_data.country_name = country_data.country_name.apply(
            lambda x: x if self.un_to_dit_country_map.get(x) is None else self.un_to_dit_country_map.get(x)
        )
        return country_data

    def get_population_data(self, country, target_ages):
        population_data = {
            'country': country,
            'target_ages': target_ages,
            'year': self.year,
        }

        mapped_target_age_groups = self.get_mapped_age_groups(target_ages)

        population_data.update(self.get_population_target_age_sex_data(
            country=country, target_ages=mapped_target_age_groups, sex='male')
        )
        population_data.update(
            self.get_population_target_age_sex_data(country=country, target_ages=mapped_target_age_groups, sex='female')
        )
        population_data.update(self.get_population_urban_rural_data(country=country, classification='urban'))
        population_data.update(self.get_population_urban_rural_data(country=country, classification='rural'))
        population_data.update(self.get_population_total_data(country=country))
        if all([
                population_data.get('urban_population_total'),
                population_data.get('rural_population_total'),
                population_data.get('total_population'),
            ]
        ):
            population_data['urban_percentage'] = round(
                population_data['urban_population_total']/population_data['total_population'], 6
            )
            population_data['rural_percentage'] = 1 - population_data['urban_percentage']

        if population_data.get('male_target_age_population') and population_data.get('female_target_age_population'):
            population_data['total_target_age_population'] = (
                    population_data['male_target_age_population'] + population_data['female_target_age_population']
            )

        return population_data

    def get_mapped_age_groups(self, target_ages):
        # Function to convert inout target age groups to UN specfific age groups
        age_map_dict = {
            '0-14': ['0-4', '5-9', '10-14'],
            '15-19': ['15-19'],
            '20-24': ['20-24'],
            '25-34': ['25-29', '30-34'],
            '35-44': ['35-39', '40-44'],
            '45-54': ['45-49', '50-54'],
            '55-64': ['55-59', '60-64'],
            '65+': ['65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95-99', '100+'],
        }
        mapped_ages = ([age_map_dict[v] for v in target_ages if v in age_map_dict.keys()])
        return list(chain.from_iterable(mapped_ages))

    def get_population_target_age_sex_data(self, country, target_ages, sex):
        target_sex = sex.lower()
        target_age_sex_data = {}

        un_population_data = self.un_male_pop_data if target_sex == 'male' else self.un_female_pop_data
        un_data_transponsed = un_population_data.melt(
            ['country_name', 'country_code', 'year', 'type'], var_name='age_group', value_name='age_value'
        )
        country_data = un_data_transponsed[
            (un_data_transponsed.country_name == country) & (un_data_transponsed.year == self.year)
            ]
        if not country_data.empty:
            total_population_target_age = country_data[country_data.age_group.isin(target_ages)].age_value.sum()
            target_age_sex_data[f'{target_sex}_target_age_population'] = total_population_target_age
        return target_age_sex_data

    def get_population_total_data(self, country):
        total_population = {}

        un_data_transponsed = self.un_female_pop_data.melt(
            ['country_name', 'country_code', 'year', 'type'], var_name='age_group', value_name='age_value'
        )
        female_country_data = un_data_transponsed[
            (un_data_transponsed.country_name == country) & (un_data_transponsed.year == self.year)
            ]
        un_data_transponsed = self.un_male_pop_data.melt(
            ['country_name', 'country_code', 'year', 'type'], var_name='age_group', value_name='age_value'
        )
        male_country_data = un_data_transponsed[
            (un_data_transponsed.country_name == country) & (un_data_transponsed.year == self.year)
            ]

        if not male_country_data.empty and not female_country_data.empty:
            # Only send data if we found country year and data for both males/females
            total_population['total_population'] = (
                    female_country_data.age_value.sum() + male_country_data.age_value.sum()
            )
        return total_population

    def get_population_urban_rural_data(self, country, classification):
        urban_rural_data = {}
        target_classification = classification.lower()
        un_population_data = self.un_urban_pop if target_classification == 'urban' else self.un_rural_pop
        un_data_transponsed = un_population_data.melt(
            ['country_name', 'country_code', ], var_name='year', value_name='year_value'
        )
        classified_data = un_data_transponsed[
            (un_data_transponsed.country_name == country) & (un_data_transponsed.year == str(self.year))
            ]
        if not classified_data.empty:
            urban_rural_data[f'{target_classification}_population_total'] = classified_data.year_value.sum()
        return urban_rural_data


class TTLCache:

    def __init__(self, default_cache_max_age=60 * 60 * 24):
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


@TTLCache()
def get_world_economic_outlook_data(country_code):
    data = []
    for record in models.WorldEconomicOutlook.objects.filter(country_code=country_code):
        data.append(serializers.WorldEconomicOutlookSerializer(record).data)
    serializer = serializers.WorldEconomicOutlookSerializer(data, many=True)
    return json.loads(json.dumps(serializer.data))


@TTLCache()
def get_cia_factbook_data(country_name, data_keys=None):
    try:
        cia_data = models.CIAFactbook.objects.get(country_name=country_name).factbook_data
        if data_keys:
            cia_keys_data = dict((key, value) for key, value in cia_data.items() if key in data_keys)
            cia_data = cia_keys_data
        return cia_data
    except models.CIAFactbook.DoesNotExist:
        return {}


def get_internet_usage(country):
    try:
        internet_usage_obj = models.InternetUsage.objects.filter(
            country_name=country).latest()
    except models.InternetUsage.DoesNotExist:
        return {}
    return {
        'internet_usage': {
            'value': '{:.2f}'.format(internet_usage_obj.value) if hasattr(internet_usage_obj, 'value') else None,
            'year': internet_usage_obj.year if hasattr(internet_usage_obj, 'year') else None,
        }
    }


def get_cpi_data(country):
    try:
        cpi_obj = models.ConsumerPriceIndex.objects.filter(
            country_name=country).latest()
    except models.ConsumerPriceIndex.DoesNotExist:
        return {}
    return {
        'cpi': {
            'value': '{:.2f}'.format(cpi_obj.value) if hasattr(cpi_obj, 'value') else None,
            'year': cpi_obj.year
        }
    }


def millify(n):

    n = float(n)
    mill_names = ['', ' thousand', ' million', ' billion', ' trillion']
    mill_idx = max(0, min(len(mill_names) - 1,
                          int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.2f}{}'.format(n / 10 ** (3 * mill_idx), mill_names[mill_idx])


def get_percentage_format(number, total):
    if not number or not total:
        return
    percentage = int(number) / int(total) * 100
    mill_name = millify(number * 1000)
    return '{:.2f}% ({})'.format(percentage, mill_name)


def get_urban_rural_data(data_object, total_population, classification):
    return {
        f'{classification}_population_total': data_object.get(f'{classification}_population_total', 0),
        f'{classification}_population_percentage_formatted':
            get_percentage_format(
                data_object.get(f'{classification}_population_total', 0),
                total_population.get('total_population', 0)
            )
    }


def get_serialized_instance_from_model(
        model_class, serializer_class, filter_args):
    try:
        instance = model_class.objects.get(**filter_args)
        serializer = serializer_class(instance)
        return serializer.data
    except model_class.DoesNotExist:
        return None
