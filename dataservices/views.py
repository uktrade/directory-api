import json

from django.apps import apps
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response

from dataservices import helpers, models, serializers
from dataservices.helpers import (
    deep_extend,
    get_multiple_serialized_instance_from_model,
    get_serialized_instance_from_model,
    get_urban_rural_data,
    millify,
)
from dataservices.models import (
    ConsumerPriceIndex,
    CorruptionPerceptionsIndex,
    EaseOfDoingBusiness,
    GDPPerCapita,
    Income,
    InternetUsage,
    RuleOfLaw,
)
from dataservices.serializers import (
    ConsumerPriceIndexSerializer,
    CorruptionPerceptionsIndexSerializer,
    EaseOfDoingBusinessSerializer,
    GDPPerCapitaSerializer,
    IncomeSerializer,
    InternetUsageSerializer,
    RuleOfLawSerializer,
)


class RetrieveEaseOfBusinessIndex(generics.RetrieveAPIView):
    serializer_class = serializers.EaseOfDoingBusinessSerializer
    permission_classes = []
    lookup_url_kwarg = 'country_code'
    lookup_field = 'country_code__iexact'
    queryset = models.EaseOfDoingBusiness.objects.all()

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(data={})
        return super().handle_exception(exc)


class RetrieveCorruptionPerceptionsIndex(generics.RetrieveAPIView):
    serializer_class = serializers.CorruptionPerceptionsIndexSerializer
    permission_classes = []
    lookup_url_kwarg = 'country_code'
    lookup_field = 'country_code__iexact'
    queryset = models.CorruptionPerceptionsIndex.objects.all()

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(data={})
        return super().handle_exception(exc)


class RetrieveWorldEconomicOutlook(generics.ListAPIView):
    serializer_class = serializers.WorldEconomicOutlookSerializer
    permission_classes = []

    def get_queryset(self):
        country_code = self.kwargs['country_code']
        return models.WorldEconomicOutlook.objects.filter(country_code=country_code)

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(data={})
        return super().handle_exception(exc)


class RetrieveLastYearImportDataView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        commodity_code = self.request.GET.get('commodity_code', '')
        country = self.request.GET.get('country', '')
        comtrade_response = helpers.get_last_year_import_data(commodity_code=commodity_code, country=country)
        return Response(status=status.HTTP_200_OK, data={'last_year_data': comtrade_response})


class RetrieveLastYearImportDataFromUKView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        commodity_code = self.request.GET.get('commodity_code', '')
        country = self.request.GET.get('country', '')
        comtrade_response = helpers.get_last_year_import_data_from_uk(commodity_code=commodity_code, country=country)
        return Response(status=status.HTTP_200_OK, data={'last_year_data': comtrade_response})


class RetrieveLastYearImportDataByCountryView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        comtrade_response = helpers.get_comtrade_data_by_country(
            commodity_code=self.request.GET.get('commodity_code', ''),
            country_list=self.request.GET.getlist('countries', ''),
        )
        return Response(status=status.HTTP_200_OK, data=comtrade_response)


class RetrieveHistoricalImportDataView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        commodity_code = self.request.GET.get('commodity_code', '')
        country = self.request.GET.get('country', '')

        comtrade = helpers.ComTradeData(commodity_code=commodity_code, reporting_area=country)

        historical_data = comtrade.get_all_historical_import_value()
        return Response(status=status.HTTP_200_OK, data=historical_data)


class RetrieveCountryDataView(generics.GenericAPIView):
    dit_to_weo_country_map = {
        'Brunei': 'Brunei Darussalam',
        'Congo': 'Congo, Rep.',
        'Congo (Democratic Republic)': ['Congo, Dem. Rep.', 'Democratic Republic of the Congo'],
        'Dominican': 'Dominican Republic',
        'Egypt': ['Egypt, Arab Rep.', 'Egypt'],
        'Micronesia': 'Micronesia, Fed. Sts.',
        'Myanmar (Burma)': 'Myanmar',
        'St Kitts and Nevis': 'St. Kitts and Nevis',
        'St Lucia': ['St. Lucia', 'Saint Lucia'],
        'St Vincent': ['St. Vincent and the Grenadines', 'Saint Vincent and the Grenadines'],
        'Russia': ['Russian Federation', 'Russia'],
        'Syria': ['Syrian Arab Republic', 'Syria'],
        'The Bahamas': ['Bahamas, The', 'Bahamas'],
        'The Gambia': ['Gambia, The', 'Gambia'],
        'Yemen': ['Yemen, Rep.', 'Yemen'],
        'Venezuela': ['Venezuela, RB', 'Venezuela'],
        'United States': ['United States of America', 'United States'],
    }
    permission_classes = []

    def get(self, *args, **kwargs):
        filter_args = self.get_filter(country=self.kwargs['country'])

        country_population = helpers.PopulationData()
        total_population = country_population.get_population_total_data(country=self.kwargs['country'])
        country_data = {
            'consumer_price_index': get_serialized_instance_from_model(
                ConsumerPriceIndex, ConsumerPriceIndexSerializer, filter_args
            ),
            'internet_usage': get_serialized_instance_from_model(InternetUsage, InternetUsageSerializer, filter_args),
            'corruption_perceptions_index': get_serialized_instance_from_model(
                CorruptionPerceptionsIndex, CorruptionPerceptionsIndexSerializer, filter_args
            ),
            'ease_of_doing_bussiness': get_serialized_instance_from_model(
                EaseOfDoingBusiness, EaseOfDoingBusinessSerializer, filter_args
            ),
            'gdp_per_capita': get_serialized_instance_from_model(GDPPerCapita, GDPPerCapitaSerializer, filter_args),
            'total_population': millify(total_population.get('total_population', 0) * 1000),
            'income': get_serialized_instance_from_model(Income, IncomeSerializer, filter_args),
        }
        if country_data['internet_usage']:
            total_internet_usage = helpers.calculate_total_internet_population(
                country_data['internet_usage'], total_population
            )
            country_data['internet_usage']['total_internet_usage'] = total_internet_usage

        return Response(status=status.HTTP_200_OK, data={'country_data': country_data})

    def get_filter(self, country):
        weo_country = self.dit_to_weo_country_map.get(country, country)
        return {'country_name__in': weo_country} if (type(weo_country) is list) else {'country_name': weo_country}


class RetrieveDataByCountryView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        # Will be passed a lis of countries and 'fields' === model names
        # The return is a map by countries of the serialized model instances
        countries_list = self.request.GET.getlist('countries')
        model_names = self.request.GET.getlist('fields', '')
        if len(model_names) == 1 and model_names[0][0] == '[':
            model_names = json.loads(model_names[0])
        out = {}
        for field_spec in model_names:
            filter_args = {'country__iso2__in': countries_list}
            if isinstance(field_spec, str):
                field_spec = {'model': field_spec}
            filter_args.update(field_spec.get('filter', {}))
            try:
                model = apps.get_model('dataservices', field_spec['model'])
                serializer = serializers.__dict__.get(field_spec['model'] + 'Serializer')
                if model and serializer:
                    deep_extend(
                        out,
                        get_multiple_serialized_instance_from_model(
                            model_class=model,
                            serializer_class=serializer,
                            filter_args=filter_args,
                            section_key=field_spec['model'],
                            latest_only=field_spec.get('latest_only', False),
                        ),
                    )
            except LookupError:
                pass

        return Response(status=status.HTTP_200_OK, data=out)


class RetrieveCiaFactbooklDataView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        country = self.request.GET.get('country', '')
        data_key = self.request.GET.get('data_key')
        try:
            cia_factbook_data = models.CIAFactbook.objects.get(country_name=country).factbook_data

            if data_key:
                keys = data_key.replace(' ', '').split(',')
                for k in keys:
                    if cia_factbook_data.get(k) and keys[-1] != k:
                        cia_factbook_data = cia_factbook_data[k]
                    elif cia_factbook_data.get(k):
                        # We are at the last keys lets return whole dict
                        cia_factbook_data = {k: cia_factbook_data.get(k)}
                    else:
                        cia_factbook_data = {}
        except models.CIAFactbook.DoesNotExist:
            cia_factbook_data = {}

        return Response(status=status.HTTP_200_OK, data={'cia_factbook_data': cia_factbook_data})


class RetrieveSocietyDataByCountryView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        countries = self.request.GET.getlist('countries', '')

        if not countries:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data_set = []

        for country in countries:
            country_data = {'country': country}
            society_data = helpers.get_society_data(country=country)
            ruleoflaw_data = {
                'rule_of_law': get_serialized_instance_from_model(
                    RuleOfLaw, RuleOfLawSerializer, {'country__name': country}
                )
            }

            data_set.append(
                {
                    **country_data,
                    **society_data,
                    **ruleoflaw_data,
                }
            )
        return Response(status=status.HTTP_200_OK, data=data_set)


class RetrievePopulationDataView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        target_ages = self.request.GET.getlist('target_ages', [])
        country = self.request.GET.get('country', '')
        population_data = helpers.PopulationData().get_population_data(country=country, target_ages=target_ages)
        return Response(
            status=status.HTTP_200_OK,
            data={'population_data': population_data},
        )


class RetrievePopulationDataViewByCountry(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        countries = self.request.GET.getlist('countries', '')

        if not countries:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data_set = []

        for country in countries:
            country_population = helpers.PopulationData()
            country_data = {'country': country}
            total_population = country_population.get_population_total_data(country=country)
            total_population_raw = total_population.get('total_population', 0) * 1000
            population_data = {
                'total_population': millify(total_population_raw),
                'total_population_raw': total_population_raw,
            }

            # urban population
            urban_population_data = country_population.get_population_urban_rural_data(
                country=country, classification='urban'
            )
            urban_population = get_urban_rural_data(urban_population_data, total_population, 'urban')

            # rural population
            rural_population_data = country_population.get_population_urban_rural_data(
                country=country, classification='rural'
            )
            rural_population = get_urban_rural_data(rural_population_data, total_population, 'rural')

            internet_usage = helpers.get_internet_usage(country=country)
            cpi = helpers.get_cpi_data(country=country)

            data_set.append(
                {
                    **country_data,
                    **internet_usage,
                    **rural_population,
                    **urban_population,
                    **population_data,
                    **cpi,
                }
            )
        return Response(status=status.HTTP_200_OK, data=data_set)


class SuggestedCountriesView(generics.ListAPIView):
    serializer_class = serializers.SuggestedCountrySerializer
    permission_classes = []

    def get_queryset(self):
        hs_code = self.request.query_params.get('hs_code', '').lower()
        queryset = (
            models.SuggestedCountry.objects.filter(hs_code=hs_code)
            .order_by('order')
            .values('hs_code', 'country__name', 'country__iso2', 'country__region')
        )
        return queryset

    def get(self, *args, **kwargs):
        if not self.request.query_params.get('hs_code'):
            return Response(status=500, data={'error_message': 'hs_code missing in request params'})
        return super().get(*args, **kwargs)


class TradingBlocsView(generics.ListAPIView):
    serializer_class = serializers.TradingBlocsSerializer
    permission_classes = []

    def get_queryset(self):
        iso2 = self.request.query_params.get('iso2', '').lower()
        queryset = models.TradingBlocs.objects.filter(country__iso2__iexact=iso2)
        return queryset

    def get(self, *args, **kwargs):
        if not self.request.query_params.get('iso2'):
            return Response(status=500, data={'error_message': 'Country ISO2 is missing in request params'})
        return super().get(*args, **kwargs)
