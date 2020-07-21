from rest_framework import status, generics

from dataservices import serializers, models, helpers
from rest_framework.response import Response
from django.http import Http404


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
        comtrade = helpers.ComTradeData(commodity_code=commodity_code, reporting_area=country)
        last_year_data = comtrade.get_last_year_import_data()
        return Response(
            status=status.HTTP_200_OK,
            data={'last_year_data': last_year_data}
        )


class RetrieveHistoricalImportDataView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        commodity_code = self.request.GET.get('commodity_code', '')
        country = self.request.GET.get('country', '')

        comtrade = helpers.ComTradeData(commodity_code=commodity_code, reporting_area=country)

        historical_data = comtrade.get_all_historical_import_value()
        return Response(
            status=status.HTTP_200_OK,
            data=historical_data
        )


class RetrieveCountryDataView(generics.GenericAPIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        country = self.kwargs['country']
        country_data = {'consumer_price_index': {}, 'internet_usage': {}}
        try:
            instance = models.ConsumerPriceIndex.objects.get(
                country_name=country)
            serializer = serializers.ConsumerPriceIndexSerializer(instance)

            country_data['consumer_price_index'] = serializer.data
        except models.ConsumerPriceIndex.DoesNotExist:
            pass
        try:
            instance = models.InternetUsage.objects.get(
                country_name=country)
            serializer = serializers.InternetUsageSerializer(instance)
            country_data['internet_usage'] = serializer.data
        except models.InternetUsage.DoesNotExist:
            pass

        return Response(
            status=status.HTTP_200_OK,
            data=country_data
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
                        break
                    else:
                        cia_factbook_data = {}
        except models.CIAFactbook.DoesNotExist:
            cia_factbook_data = {}

        return Response(
            status=status.HTTP_200_OK,
            data=cia_factbook_data
        )
