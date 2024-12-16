import json

from django.core.cache import cache

from dataservices import models, serializers


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


def get_comtrade_data_by_country(commodity_code, country_list):
    data = {}
    qs = models.ComtradeReport.objects.filter(country__iso2__in=country_list, commodity_code=commodity_code).order_by(
        '-year'
    )
    for record in qs:
        iso_code = record.country.iso2
        data[iso_code] = data.get(iso_code, [])
        data[iso_code].append(serializers.ComtradeReportSerializer(record).data)
    return data


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
        internet_usage_obj = models.InternetUsage.objects.filter(country__name=country).latest('year')
        return {
            'internet_usage': {
                'value': '{:.2f}'.format(internet_usage_obj.value) if hasattr(internet_usage_obj, 'value') else None,
                'year': internet_usage_obj.year if hasattr(internet_usage_obj, 'year') else None,
            }
        }
    except models.InternetUsage.DoesNotExist:
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
