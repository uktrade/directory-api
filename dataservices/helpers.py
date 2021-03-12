import json
import math
from datetime import datetime
from itertools import chain

import pandas
from django.core.cache import cache

from dataservices import models, serializers


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

        population_data.update(
            self.get_population_target_age_sex_data(country=country, target_ages=mapped_target_age_groups, sex='male')
        )
        population_data.update(
            self.get_population_target_age_sex_data(country=country, target_ages=mapped_target_age_groups, sex='female')
        )
        population_data.update(self.get_population_urban_rural_data(country=country, classification='urban'))
        population_data.update(self.get_population_urban_rural_data(country=country, classification='rural'))
        population_data.update(self.get_population_total_data(country=country))
        if all(
            [
                population_data.get('urban_population_total'),
                population_data.get('rural_population_total'),
                population_data.get('total_population'),
            ]
        ):
            population_data['urban_percentage'] = round(
                population_data['urban_population_total'] / population_data['total_population'], 6
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
        mapped_ages = [age_map_dict[v] for v in target_ages if v in age_map_dict.keys()]
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
            target_data = country_data.age_group.isin(target_ages)
            total_population_target_age = pandas.to_numeric(country_data[target_data].age_value, errors='coerce').sum()
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
            male_age_value = pandas.to_numeric(male_country_data.age_value, errors='coerce')
            female_age_value = pandas.to_numeric(female_country_data.age_value, errors='coerce')
            total_population['total_population'] = female_age_value.sum() + male_age_value.sum()
        return total_population

    def get_population_urban_rural_data(self, country, classification):
        urban_rural_data = {}
        target_classification = classification.lower()
        un_population_data = self.un_urban_pop if target_classification == 'urban' else self.un_rural_pop
        un_data_transponsed = un_population_data.melt(
            [
                'country_name',
                'country_code',
            ],
            var_name='year',
            value_name='year_value',
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


def get_comtrade_data_by_country(commodity_code, country_list):
    data = {}
    for record in models.ComtradeReport.objects.filter(country__iso2__in=country_list, commodity_code=commodity_code):
        iso_code = record.country.iso2
        data[iso_code] = data.get(iso_code, [])
        data[iso_code].append(serializers.ComTradeReportSerializer(record).data)
    return data


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


@TTLCache()
def get_internet_usage(country):
    try:
        internet_usage_obj = models.InternetUsage.objects.filter(country_name=country).latest()
        return {
            'internet_usage': {
                'value': '{:.2f}'.format(internet_usage_obj.value) if hasattr(internet_usage_obj, 'value') else None,
                'year': internet_usage_obj.year if hasattr(internet_usage_obj, 'year') else None,
            }
        }
    except Exception:
        return {}


@TTLCache()
def get_cpi_data(country):
    try:
        cpi_obj = models.ConsumerPriceIndex.objects.filter(country_name=country).latest('year')
        return {
            'cpi': {
                'value': '{:.2f}'.format(cpi_obj.value) if hasattr(cpi_obj, 'value') else None,
                'year': cpi_obj.year,
            }
        }
    except Exception:
        return {}


@TTLCache()
def get_society_data(country):
    society_data = {}
    cia_people_data = get_cia_factbook_data(country, data_keys=['people'])

    if not cia_people_data:
        return society_data

    cia_people_data = cia_people_data.get('people')

    society_data['religions'] = cia_people_data.get('religions', {})
    society_data['languages'] = cia_people_data.get('languages', {})

    return society_data


def deep_extend(o1, o2):
    # Deep extend dict o2 onto o1.  o1 is mutated
    for key, value in o2.items():
        if o1.get(key) and isinstance(o1.get(key), dict) and isinstance(value, dict):
            deep_extend(o1.get(key), value)
        else:
            o1[key] = value
    return o1


def millify(n):
    n = float(n)
    mill_names = ['', ' thousand', ' million', ' billion', ' trillion']
    mill_idx = max(0, min(len(mill_names) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
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
        f'{classification}_population_percentage_formatted': get_percentage_format(
            data_object.get(f'{classification}_population_total', 0), total_population.get('total_population', 0)
        ),
    }


def get_serialized_instance_from_model(model_class, serializer_class, filter_args):
    fields = [field.name for field in model_class._meta.fields]
    results = model_class.objects.filter(**filter_args)
    if 'year' in fields:
        results = results.order_by('-year')
    for instance in results:
        serializer = serializer_class(instance)
        return serializer.data


def get_multiple_serialized_instance_from_model(model_class, serializer_class, filter_args, section_key, latest_only):
    out = {}
    fields = [field.name for field in model_class._meta.fields]

    results = model_class.objects.filter(**filter_args)
    if latest_only and 'year' in fields:
        results = results.order_by('-year')

    if results:
        for result in results:
            iso = result.country.iso2
            serialized = serializer_class(result).data
            out[iso] = out.get(iso, {section_key: []})
            if latest_only and out[iso][section_key]:
                # We only want the latest, and we have a row - let's see if the new row matches year
                if out[result.country.iso2][section_key][0].get('year') != serialized.get('year'):
                    break
            out[iso][section_key].append(serialized)
    return out


def calculate_total_internet_population(internet_usage, total_population):
    if internet_usage and total_population:
        percent = float(internet_usage.get('value')) / 100
        total = total_population.get('total_population', 0) * 1000
        return millify(percent * total)
    else:
        return ''
