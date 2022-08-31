import json

from django.apps import apps
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from dataservices import filters, helpers, models, serializers
from dataservices.core import client_api
from dataservices.helpers import (
    deep_extend,
    get_multiple_serialized_instance_from_model,
    get_serialized_instance_from_model,
)
from dataservices.models import Country, RuleOfLaw
from dataservices.serializers import RuleOfLawSerializer


class RetrieveLastYearImportDataByCountryView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        comtrade_response = helpers.get_comtrade_data_by_country(
            commodity_code=self.request.GET.get('commodity_code', ''),
            country_list=self.request.GET.getlist('countries', ''),
        )
        return Response(status=status.HTTP_200_OK, data=comtrade_response)


class RetrieveDataByCountryView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        # Will be passed a list of countries and 'fields' === model names
        # The return is a map by countries of the serialized model instances
        countries_list = self.request.GET.getlist('countries')
        model_names = self.request.GET.getlist('fields', '')
        if len(model_names) == 1 and model_names[0][0] == '[':
            model_names = json.loads(model_names[0])
        out = {}
        for field_spec in model_names:
            filter_args = {'country__iso2__in': countries_list, 'country__is_active': True}
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


class TradeBarriersView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):

        iso2_countries = self.request.query_params.getlist('countries')
        sectors = self.request.query_params.getlist('sectors')
        filters = {'locations': {}}
        for country in Country.objects.filter(iso2__in=iso2_countries):
            filters['locations'][country.iso2] = country.name
        if sectors:
            filters['sectors'] = sectors
        barriers_list = client_api.trade_barrier_data_gateway.barriers_list(filters=filters)
        return Response(status=status.HTTP_200_OK, data=barriers_list)


class MetadataMixin:
    METADATA_DATA_SOURCE_NOTES = None
    METADATA_DATA_RESOLUTION = 'quarter'

    limit = None
    reference_period = False

    def get_country(self):
        iso2 = self.request.query_params.get('iso2', '')
        country = get_object_or_404(models.Country, iso2__iexact=iso2)

        return {'country': {'name': country.name, 'iso2': country.iso2}}

    def get_reference_period(self):
        if not self.reference_period:
            return {}

        year, period = self.queryset.get_current_period().values()

        return {
            'reference_period': {
                'resolution': self.METADATA_DATA_RESOLUTION,
                'period': period,
                'year': year,
            }
        }

    def get_metadata(self):
        country = self.get_country()
        reference_period = self.get_reference_period()

        try:
            metadata = models.Metadata.objects.get(view_name=self.__class__.__name__)
        except models.Metadata.DoesNotExist:
            return country | reference_period

        return metadata.data | country | reference_period

    def get(self, *args, **kwargs):
        res = super().get(*args, **kwargs)
        data = res.data
        metadata = self.get_metadata()

        if isinstance(data, list):
            data = data[: self.limit]

        res.data = {
            'metadata': metadata,
            'data': data,
        }

        return res


class TopFiveGoodsExportsByCountryView(MetadataMixin, generics.ListAPIView):
    permission_classes = []
    queryset = models.UKTradeInGoodsByCountry.objects
    serializer_class = serializers.UKTopFiveGoodsExportsSerializer
    filter_class = filters.UKTopFiveGoodsExportsFilter
    limit = 5
    reference_period = True

    def get_queryset(self):
        return self.queryset.top_goods_exports()


class TopFiveServicesExportsByCountryView(MetadataMixin, generics.ListAPIView):
    permission_classes = []
    queryset = models.UKTradeInServicesByCountry.objects
    serializer_class = serializers.UKTopFiveServicesExportSerializer
    filter_class = filters.UKTopFiveServicesExportsFilter
    limit = 5
    reference_period = True

    def get_queryset(self):
        return self.queryset.top_services_exports()


class UKMarketTrendsView(MetadataMixin, generics.ListAPIView):
    METADATA_DATA_SOURCE_NOTES = [
        'Total trade is the sum of all exports and imports over the same time period.',
        'Data includes goods and services combined.',
    ]

    permission_classes = []
    queryset = models.UKTotalTradeByCountry.objects
    serializer_class = serializers.UKMarketTrendsSerializer
    filter_class = filters.UKMarketTrendsFilter

    def get_queryset(self):
        return self.queryset.market_trends()


class UKTradeHighlightsView(MetadataMixin, generics.RetrieveAPIView):
    # NOTE: this note could be dynamic, as it depends on the reference period
    METADATA_DATA_SOURCE_NOTES = [
        'Data includes goods and services combined in the four quarters to the end of Q4 2021.'
    ]

    permission_classes = []
    queryset = models.UKTotalTradeByCountry.objects
    serializer_class = serializers.UKTradeHighlightsSerializer
    filter_class = filters.UKTradeHighlightsFilter
    lookup_field = 'country__iso2'
    reference_period = True

    def dispatch(self, *args, **kwargs):
        kwargs[self.lookup_field] = self.request.GET.get('iso2', '').upper()

        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().highlights()


class EconomicHighlightsView(MetadataMixin, generics.RetrieveAPIView):
    permission_classes = []
    queryset = models.WorldEconomicOutlookByCountry.objects
    serializer_class = serializers.EconomicHighlightsSerializer
    filter_class = filters.EconomicHighlightsFilter
    lookup_field = 'country__iso2'

    def get_uk_stats(self, gdp_year, economic_growth_year):
        queryset = self.queryset.stats(gdp_year=gdp_year, economic_growth_year=economic_growth_year).filter(
            country__iso2='GB'
        )
        serializer = self.get_serializer(queryset, many=True)
        data = {}

        for obj in serializer.data:
            data.update(obj)

        return {'uk_data': data}

    def get(self, *args, **kwargs):
        res = super().get(*args, **kwargs)
        data = res.data['data']
        metadata = res.data['metadata']
        uk_data = self.get_uk_stats(
            gdp_year=data['gdp_per_capita']['year'], economic_growth_year=data['economic_growth']['year']
        )

        res.data['metadata'] = metadata | uk_data

        return res

    def retrieve(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = {}

        for obj in serializer.data:
            data.update(obj)

        return Response(data)

    def dispatch(self, *args, **kwargs):
        kwargs[self.lookup_field] = self.request.GET.get('iso2', '').upper()

        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().stats()
