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
