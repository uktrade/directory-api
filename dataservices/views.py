import json

from django.apps import apps
from django.db.models import Avg, Max, Sum
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema, inline_serializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.serializers import CharField

from dataservices import filters, helpers, models, renderers, serializers
from dataservices.core import client_api
from dataservices.helpers import (
    deep_extend,
    get_multiple_serialized_instance_from_model,
    get_serialized_instance_from_model,
)
from dataservices.models import Country, RuleOfLaw
from dataservices.serializers import RuleOfLawSerializer


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={
                '<iso2>': [
                    {
                        'year': 'integer',
                        'classification': 'string',
                        'uk_or_world': 'string',
                        'commodity_code': 'string',
                        'trade_value': 'double',
                    },
                    {
                        'year': 'integer',
                        'classification': 'string',
                        'uk_or_world': 'string',
                        'commodity_code': 'string',
                        'trade_value': 'double',
                    },
                ]
            },
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Last Year Import Data By Country',
    parameters=[
        OpenApiParameter(name='commodity_code', description='Commodity Code', required=True, type=str),
        OpenApiParameter(
            name='countries',
            description='Countries',
            required=True,
            type={'type': 'array', 'items': {'type': 'string'}},
        ),
    ],
)
class RetrieveLastYearImportDataByCountryView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        comtrade_response = helpers.get_comtrade_data_by_country(
            commodity_code=self.request.GET.get('commodity_code', ''),
            country_list=self.request.GET.getlist('countries', ''),
        )
        return Response(status=status.HTTP_200_OK, data=comtrade_response)


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={
                '<data_key1>': {
                    '<field1>': [
                        {'value': 'double', 'year': 'integer'},
                        {'value': 'double', 'year': 'integer'},
                    ],
                    '<field2>': [
                        {'urban_rural': 'string', 'value': 'integer', 'year': 'integer'},
                        {'urban_rural': 'string', 'value': 'integer', 'year': 'integer'},
                    ],
                },
                '<data_key2>': {
                    '<field1>': [
                        {'value': 'double', 'year': 'integer'},
                        {'value': 'double', 'year': 'integer'},
                    ],
                    '<field2>': [
                        {'urban_rural': 'string', 'value': 'double', 'year': 'integer'},
                        {'urban_rural': 'string', 'value': 'double', 'year': 'integer'},
                    ],
                },
            },
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Country Data',
    parameters=[
        OpenApiParameter(
            name='countries',
            description='Country ISO2',
            required=True,
            type={'type': 'array', 'items': {'type': 'string'}},
        ),
        OpenApiParameter(
            name='fields', description='Fields', required=True, type={'type': 'array', 'items': {'type': 'string'}}
        ),
    ],
)
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


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={
                "data": [
                    {
                        "reference_id": "string",
                        "name": "string",
                        "type": "string",
                        "iso1_code": "string",
                        "iso2_code": "string",
                        "iso3_code": "string",
                        "overseas_region_overseas_region_name": "string",
                        "start_date": "date",
                        "end_date": "date",
                        "region": "string",
                    }
                ]
            },
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Markets',
)
class RetrieveMarketsView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        markets_data = models.Market.objects.values(
            'reference_id',
            'name',
            'type',
            'iso1_code',
            'iso2_code',
            'iso3_code',
            'overseas_region_overseas_region_name',
            'start_date',
            'end_date',
            'enabled',
        )

        return Response(status=status.HTTP_200_OK, data=markets_data)


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={'cia_factbook_data': {'key': 'string|list'}},
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Cia Factbookl Data',
    parameters=[
        OpenApiParameter(name='country', description='Country', required=True, type=str),
        OpenApiParameter(name='data_key', description='Data Key', required=False, type=str),
    ],
)
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


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value=[
                {
                    'country': 'string',
                    'religions': {
                        'date': 'integer',
                        'note': 'string',
                        'religion': [{'name': 'string', 'note': 'string'}],
                    },
                    'languages': {
                        'note': 'string',
                        'language': [
                            {'   name': 'string', 'note': 'string', 'percent': 'integer'},
                            {'name': 'string', 'note': 'string'},
                        ],
                    },
                    'rule_of_law': {
                        'year': 'integer',
                        'country_name': 'string',
                        'iso2': 'string',
                        'rank': 'integer',
                        'score': 'double',
                    },
                }
            ],
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Society Data By Country',
    parameters=[
        OpenApiParameter(
            name='countries',
            description='Countries',
            required=True,
            type={'type': 'array', 'items': {'type': 'string'}},
        ),
    ],
)
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


@extend_schema(
    responses={
        200: inline_serializer(
            name='SuggestedCountries200Response',
            fields={
                'hs_code': CharField(),
                'country__name': CharField(),
                'country__iso2': CharField(),
                'country__region': CharField(),
            },
        ),
        500: inline_serializer(
            name='SuggestedCountries500Response',
            fields={'error_message': CharField(default='hs_code missing in request params')},
        ),
    },
    description='Suggested Countries',
    parameters=[OpenApiParameter(name='hs_code', description='hs_code', required=True, type=str)],
)
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


@extend_schema(
    responses=serializers.TradingBlocsSerializer,
    description='Trading Blocs',
    parameters=[OpenApiParameter(name='iso2', description='Country ISO2', required=True, type=str)],
)
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


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={
                '<iso2>': {
                    'barriers': [
                        {
                            'id': 'string',
                            'title': 'string',
                            'summary': 'string',
                            'is_resolved': 'boolean',
                            'status_date': 'date',
                            'country': {
                                'name': 'string',
                                'trading_bloc': {
                                    'code': 'string',
                                    'name': 'string',
                                    'short_name': 'string',
                                    'overseas_regions': [{'name': 'string', 'id': 'guid'}],
                                },
                            },
                            'caused_by_trading_bloc': 'boolean',
                            'trading_bloc': {
                                'code': 'string',
                                'name': 'string',
                                'short_name': 'string',
                                'overseas_regions': [{'name': 'string', 'id': 'guid'}],
                            },
                            'location': 'string',
                            'sectors': [{'name': 'string'}],
                            'categories': [{}],
                            'last_published_on': 'datetime',
                            'reported_on': 'datetime',
                        }
                    ],
                    'count': 'integer',
                }
            },
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Trading Barriers',
    parameters=[
        OpenApiParameter(
            name='countries',
            description='Country ISO2',
            required=True,
            type={'type': 'array', 'items': {'type': 'string'}},
        ),
        OpenApiParameter(
            name='sectors', description='Sectors', required=True, type={'type': 'array', 'items': {'type': 'string'}}
        ),
    ],
)
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
    METADATA_DATA_RESOLUTION = 'quarter'

    limit = None
    reference_period = False

    def get_country(self):
        iso2 = self.request.query_params.get('iso2', '')
        if not iso2:
            return {}

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['metadata'] = self.get_metadata()

        return context


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={
                'metadata': {
                    'source': {
                        'url': 'string',
                        'label': 'string',
                        'last_release': 'date time',
                        'organisation': 'string',
                    },
                    'country': {'name': 'string', 'iso2': 'string'},
                    'reference_period': {'resolution': 'string', 'period': 'integer', 'year': 'integer'},
                },
                'data': [
                    {'label': 'string', 'value': 'integer'},
                    {'label': 'string', 'value': 'integer'},
                    {'label': 'string', 'value': 'integer'},
                    {'label': 'string', 'value': 'integer'},
                    {'label': 'string', 'value': 'integer'},
                ],
            },
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Top Five Goods Exports By Country',
    parameters=[OpenApiParameter(name='iso2', description='Country ISO2', required=True, type=str)],
)
class TopFiveGoodsExportsByCountryView(MetadataMixin, generics.ListAPIView):
    permission_classes = []
    queryset = models.UKTradeInGoodsByCountry.objects
    serializer_class = serializers.UKTopFiveGoodsExportsSerializer
    filterset_class = filters.UKTopFiveGoodsExportsFilter
    renderer_classes = (renderers.CustomDataMetadataJSONRenderer,)
    limit = 5
    reference_period = True

    def get_queryset(self):
        return self.queryset.top_goods_exports()


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={
                'metadata': {
                    'source': {
                        'url': 'string',
                        'label': 'string',
                        'last_release': 'date time',
                        'organisation': 'string',
                    },
                    'country': {'name': 'string', 'iso2': 'string'},
                    'reference_period': {'resolution': 'string', 'period': 'integer', 'year': 'integer'},
                },
                'data': [
                    {'label': 'string', 'value': 'integer'},
                    {'label': 'string', 'value': 'integer'},
                    {'label': 'string', 'value': 'integer'},
                    {'label': 'string', 'value': 'integer'},
                    {'label': 'string', 'value': 'integer'},
                ],
            },
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Top Five Services Exports By Country',
    parameters=[OpenApiParameter(name='iso2', description='Country ISO2', required=True, type=str)],
)
class TopFiveServicesExportsByCountryView(MetadataMixin, generics.ListAPIView):
    permission_classes = []
    queryset = models.UKTradeInServicesByCountry.objects
    serializer_class = serializers.UKTopFiveServicesExportSerializer
    filterset_class = filters.UKTopFiveServicesExportsFilter
    renderer_classes = (renderers.CustomDataMetadataJSONRenderer,)
    limit = 5
    reference_period = True

    def get_queryset(self):
        return self.queryset.top_services_exports()


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={
                'metadata': {
                    'source': {
                        'url': 'string',
                        'label': 'string',
                        'last_release': 'date time',
                        'organisation': 'string',
                    },
                    'country': {'name': 'string', 'iso2': 'string'},
                },
                'data': [
                    {
                        'year': 'integer',
                        'imports': 'integer',
                        'exports': 'integer',
                    },
                    {
                        'year': 'integer',
                        'imports': 'integer',
                        'exports': 'integer',
                    },
                    {
                        'year': 'integer',
                        'imports': 'integer',
                        'exports': 'integer',
                    },
                ],
            },
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='UK Market Trends',
    parameters=[
        OpenApiParameter(name='iso2', description='Country ISO2', required=True, type=str),
        OpenApiParameter(name='from_year', description='From Year', required=False, type=int),
    ],
)
class UKMarketTrendsView(MetadataMixin, generics.ListAPIView):
    permission_classes = []
    queryset = models.UKTotalTradeByCountry.objects
    serializer_class = serializers.UKMarketTrendsSerializer
    filterset_class = filters.UKMarketTrendsFilter
    renderer_classes = (renderers.CustomDataMetadataJSONRenderer,)

    def get_queryset(self):
        return self.queryset.market_trends()


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={
                'metadata': {
                    'source': {
                        'url': 'string',
                        'label': 'string',
                        'last_release': 'datetime',
                        'organisation': 'string',
                    },
                    'country': {'name': 'string', 'iso2': 'string'},
                    'reference_period': {'resolution': 'string', 'period': 'integer', 'year': 'integer'},
                },
                'data': {
                    'total_uk_exports': 'integer',
                    'trading_position': 'integer',
                    'percentage_of_uk_trade': 'double',
                },
            },
        )
    ],
    description='UK Trade Highlights',
    parameters=[OpenApiParameter(name='iso2', description='Country ISO2', required=True, type=str)],
)
class UKTradeHighlightsView(MetadataMixin, generics.RetrieveAPIView):
    permission_classes = []
    queryset = models.UKTotalTradeByCountry.objects
    serializer_class = serializers.UKTradeHighlightsSerializer
    filterset_class = filters.UKTradeHighlightsFilter
    renderer_classes = (renderers.CustomDataMetadataJSONRenderer,)
    lookup_field = 'country__iso2'
    reference_period = True

    def dispatch(self, *args, **kwargs):
        kwargs[self.lookup_field] = self.request.GET.get('iso2', '').upper()

        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().highlights()


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={
                'metadata': {
                    'source': {
                        'url': 'string',
                        'label': 'string',
                        'last_release': 'datetime',
                        'organisation': 'string',
                    },
                    'country': {'name': 'string', 'iso2': 'string'},
                    'uk_data': {
                        'gdp_per_capita': {'year': 'integer', 'value': 'integer', 'is_projection': 'boolean'},
                        'market_position': {
                            'year': 'integer',
                            'value': 'integer',
                            'is_projection': 'boolean',
                        },
                        'economic_growth': {
                            'year': 'integer',
                            'value': 'float',
                            'is_projection': 'boolean',
                        },
                    },
                },
                'data': {
                    'gdp_per_capita': {'year': 'integer', 'value': 'integer', 'is_projection': 'boolean'},
                    'market_position': {
                        'year': 'integer',
                        'value': 'integer',
                        'is_projection': 'boolean',
                    },
                    'economic_growth': {
                        'year': 'integer',
                        'value': 'float',
                        'is_projection': 'boolean',
                    },
                },
            },
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Economic Highlights',
    parameters=[OpenApiParameter(name='iso2', description='Country ISO2', required=True, type=str)],
)
class EconomicHighlightsView(MetadataMixin, generics.RetrieveAPIView):
    permission_classes = []
    queryset = models.WorldEconomicOutlookByCountry.objects
    serializer_class = serializers.EconomicHighlightsSerializer
    filterset_class = filters.EconomicHighlightsFilter
    renderer_classes = (renderers.CustomDataMetadataJSONRenderer,)
    lookup_field = 'country__iso2'

    def get_uk_stats(self, mkt_pos_year, gdp_per_capita_year, economic_growth_year):
        queryset = self.queryset.stats(
            mkt_pos_year=mkt_pos_year,
            gdp_per_capita_year=gdp_per_capita_year,
            economic_growth_year=economic_growth_year,
        ).filter(country__iso2='GB')

        serializer = self.get_serializer(queryset, many=True)
        data = {k: v for element in serializer.data for k, v in element.items()}

        return {'uk_data': data}

    def retrieve(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = {k: v for element in serializer.data for k, v in element.items()}

        if data:
            self.kwargs['extra_metadata'] = self.get_uk_stats(
                mkt_pos_year=data['market_position']['year'],
                gdp_per_capita_year=data['gdp_per_capita']['year'],
                economic_growth_year=data['economic_growth']['year'],
            )

        return Response(data)

    def dispatch(self, *args, **kwargs):
        kwargs[self.lookup_field] = self.request.GET.get('iso2', '').upper()

        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().stats()


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={
                'data': [
                    'Australia',
                    'Japan Comprehensive Economic Partnership Agreement',
                    'New Zealand',
                    'Singapore Digital Economy Agreement',
                ]
            },
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='UK Free Trade Agreements',
)
class UKFreeTradeAgreementsView(generics.ListAPIView):
    permission_classes = []
    queryset = models.UKFreeTradeAgreement.objects
    serializer_class = serializers.UKFreeTradeAgreementSerializer

    def list(self, *args, **kwargs):
        res = super().list(*args, **kwargs)
        res.data = {'data': res.data}

        return res


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value=[
                {
                    'geo_description': 'England',
                    'geo_code': 'E92000001',
                    'sic_code': '95110',
                    'sic_description': 'Repair of computers and peripheral equipment',
                    'total_business_count': 4020,
                    'business_count_release_year': 2023,
                    'total_employee_count': 31000,
                    'employee_count_release_year': 2023,
                    'dbt_full_sector_name': 'Technology and smart cities : Hardware',
                    'dbt_sector_name': 'Technology and smart cities',
                }
            ],
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Business Cluster Information by SIC code',
    parameters=[
        OpenApiParameter(name='sic_code', description='SIC code', required=True, type=str),
        OpenApiParameter(name='geo_code', description='Comma separated geographic codes', required=False, type=str),
    ],
)
class BusinessClusterInformationBySicView(generics.ListAPIView):
    permission_classes = []
    serializer_class = serializers.BusinessClusterInformationSerializer
    queryset = models.EYBBusinessClusterInformation.objects
    filterset_class = filters.BusinessClusterInformationBySicFilter


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value=[
                {
                    'geo_description': 'England',
                    'geo_code': 'E92000001',
                    'total_business_count': 4020,
                    'business_count_release_year': 2023,
                    'total_employee_count': 31000,
                    'employee_count_release_year': 2023,
                    'dbt_sector_name': 'Technology and smart cities',
                }
            ],
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Business Cluster Information by DBT Sector',
    parameters=[
        OpenApiParameter(name='sic_code', description='SIC code', required=True, type=str),
        OpenApiParameter(name='geo_code', description='Comma separated geographic codes', required=False, type=str),
    ],
)
class BusinessClusterInformationByDBTSectorView(generics.ListAPIView):
    # view that aggregates data across a geographic region / DBT Sector (which spans multiple sic codes)
    permission_classes = []
    serializer_class = serializers.BusinessClusterInformationAggregatedDataSerializer
    queryset = (
        models.EYBBusinessClusterInformation.objects.values(
            'geo_code',
            'geo_description',
            'dbt_sector_name',
            'business_count_release_year',
            'employee_count_release_year',
            'dbt_sector_name',
        )
        .annotate(
            total_business_count=Sum('total_business_count'),
            total_employee_count=Sum('total_employee_count'),
        )
        .order_by()
    )
    filterset_class = filters.BusinessClusterInformationByDBTSectorFilter


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value=[
                {
                    "geo_description": "East Midlands",
                    "vertical": "Finance and Professional Services",
                    "professional_level": "Director/Executive",
                    "median_salary": 48028,
                    "dataset_year": 2022,
                },
                {
                    "geo_description": "East Midlands",
                    "vertical": "Finance and Professional Services",
                    "professional_level": "Entry-level",
                    "median_salary": 23678,
                    "dataset_year": 2022,
                },
                {
                    "geo_description": "East Midlands",
                    "vertical": "Finance and Professional Services",
                    "professional_level": "Middle/Senior Management",
                    "median_salary": 33343,
                    "dataset_year": 2022,
                },
            ],
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Median salary data by region and optionally, vertical and profession level',
    parameters=[
        OpenApiParameter(
            name='geo_description',
            description='Geographic Region',
            required=True,
            type=str,
            examples=[OpenApiExample('East Midlands', value='East Midlands')],
        ),
        OpenApiParameter(
            name='vertical',
            description='Industry',
            required=False,
            type=str,
            examples=[OpenApiExample('Finance and Professional Services', value='Finance and Professional Services')],
        ),
        OpenApiParameter(
            name='professional_level',
            description='Professional level',
            required=False,
            type=str,
            examples=[OpenApiExample('Middle/Senior Management', value='Middle/Senior Management')],
        ),
    ],
)
class EYBSalaryDataView(generics.ListAPIView):
    permission_classes = []
    serializer_class = serializers.EYBSalaryDataSerializer
    filterset_class = filters.EYBSalaryFilter

    def get_queryset(self):
        """
        The salary data for geo_description/vertical/soc_code combinations contains different dataset years. Each
        combination should only be considered once when taking the average median value for a set of data at a given
        professional level, e.g. Entry-level. The below approach accomodates this by only selecting the latest data
        for each combination and is in line with the performance consideraions mentioned here
        https://docs.djangoproject.com/en/5.0/ref/models/querysets/#in
        """

        latest_data_for_each_soc_code_ids = (
            models.EYBSalaryData.objects.values('geo_description', 'vertical', 'soc_code')
            .filter(median_salary__gt=0)
            .annotate(dataset_year=Max('dataset_year'), id=Max('id'))
            .order_by()
            .values_list('id', flat=True)
        )

        queryset = (
            models.EYBSalaryData.objects.values(
                'geo_description',
                'vertical',
                'professional_level',
            )
            .filter(id__in=list(latest_data_for_each_soc_code_ids))
            .annotate(median_salary=Avg('median_salary'), dataset_year=Max('dataset_year'))
            .order_by()
        )

        return queryset


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value=[
                {
                    "geo_description": "London",
                    "vertical": "Industrial",
                    "sub_vertical": "Large Warehouses",
                    "gbp_per_square_foot_per_month": "2.292",
                    "square_feet": "340000.000",
                    "gbp_per_month": "779166.667",
                    "dataset_year": 2023,
                },
                {
                    "geo_description": "London",
                    "vertical": "Industrial",
                    "sub_vertical": "Small Warehouses",
                    "gbp_per_square_foot_per_month": "1.863",
                    "square_feet": "5000.000",
                    "gbp_per_month": "9317.130",
                    "dataset_year": 2023,
                },
                {
                    "geo_description": "London",
                    "vertical": "Retail",
                    "sub_vertical": "High Street Retail",
                    "gbp_per_square_foot_per_month": "74.722",
                    "square_feet": "2195.000",
                    "gbp_per_month": "164015.278",
                    "dataset_year": 2023,
                },
                {
                    "geo_description": "London",
                    "vertical": "Retail",
                    "sub_vertical": "Prime shopping centre",
                    "gbp_per_square_foot_per_month": "14.443",
                    "square_feet": "2195.000",
                    "gbp_per_month": "31702.791",
                    "dataset_year": 2023,
                },
                {
                    "geo_description": "London",
                    "vertical": "Office",
                    "sub_vertical": "Work Office",
                    "gbp_per_square_foot_per_month": "8.684",
                    "square_feet": "16671.000",
                    "gbp_per_month": "144770.269",
                    "dataset_year": 2023,
                },
            ],
            response_only=True,
            status_codes=[200],
        ),
    ],
    description='Median salary data by region and optionally, vertical and profession level',
    parameters=[
        OpenApiParameter(
            name='geo_description',
            description='Geographic Region',
            required=True,
            type=str,
            examples=[OpenApiExample('London', value='London')],
        ),
        OpenApiParameter(
            name='vertical',
            description='Property type',
            required=False,
            type=str,
            examples=[OpenApiExample('Industrial', value='Industrial')],
        ),
        OpenApiParameter(
            name='sub_vertical',
            description='Sub-category within vertical',
            required=False,
            type=str,
            examples=[OpenApiExample('Large Warehouse', value='Large Warehouse')],
        ),
    ],
)
class EYBRentDataView(generics.ListAPIView):
    permission_classes = []
    serializer_class = serializers.EYBCommercialRentDataSerializer
    filterset_class = filters.EYBCommercialRentDataFilter
    queryset = models.EYBCommercialPropertyRent.objects.all()
