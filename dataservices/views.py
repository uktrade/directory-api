import json

from django.apps import apps
from django.conf import settings
from rest_framework import generics, status, views
from rest_framework.response import Response

from dataservices import helpers, models, serializers
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


class CommodityExportsView(generics.ListAPIView):
    serializer_class = serializers.CommodityExportsSerializer
    permission_classes = []

    def get_queryset(self):
        iso2 = self.request.query_params.get('iso2').lower()
        queryset = models.CommodityExports.objects.filter(country__iso2__iexact=iso2)
        return queryset

    def get(self, *args, **kwargs):
        iso2 = self.request.query_params.get('iso2', '')
        if not iso2:
            return Response(status=400, data={'error_message': 'Country ISO2 is missing in request params'})
        return super().get(*args, **kwargs)


class UKTradeInServiceByCountryView(generics.ListAPIView):
    serializer_class = serializers.UKTradeInServiceByCountrySerializer
    permission_classes = []

    def get_queryset(self):
        iso2 = self.request.query_params.get('iso2').lower()
        queryset = models.UKTradeInServiceByCountry.objects.filter(country__iso2__iexact=iso2)
        return queryset

    def get(self, *args, **kwargs):
        iso2 = self.request.query_params.get('iso2', '')
        if not iso2:
            return Response(status=400, data={'error_message': 'Country ISO2 is missing in request params'})

class UKTotalTradeView(generics.ListAPIView):
    serializer_class = serializers.UKTotalTradeSerializer
    permission_classes = []

    def get_flow_type(self, queryset):
        if self.request.query_params.get('type') == 'imports':
            queryset = queryset.imports()
        elif self.request.query_params.get('type') == 'exports':
            queryset = queryset.exports()

        return queryset

    def get_product_type(self, queryset):
        if self.request.query_params.get('product') == 'goods':
            queryset = queryset.goods()
        elif self.request.query_params.get('product') == 'services':
            queryset = queryset.services()

        return queryset

    def get_year(self, queryset):
        if self.request.query_params.get('from_year'):
            return queryset.filter(year__gte=self.request.query_params['from_year'])

    def get_queryset(self):
        iso2 = self.request.query_params.get('iso2', '').upper()
        queryset = models.UKTotalTrade.objects.filter(country__iso2__iexact=iso2)

        # Param filters
        queryset = self.get_flow_type(queryset)
        queryset = self.get_product_type(queryset)
        # queryset = self.get_year(queryset)

        return queryset

    def get(self, *args, **kwargs):
        iso2 = self.request.query_params.get('iso2')
        if not iso2:
            return Response(status=400, data={'error_message': 'Country ISO2 is missing in request params'})

        res = super().get(*args, **kwargs)
        res.data = {'meta': {'iso2': iso2, 'source': settings.UK_TOTAL_TRADE_BY_COUNTRY_FILE_URL}, 'data': res.data}

        return res
