from rest_framework import serializers

from dataservices import models


class EaseOfDoingBusinessSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = models.EaseOfDoingBusiness
        exclude = ['created', 'id', 'modified']

    def get_total(self, obj):
        return models.EaseOfDoingBusiness.objects.all().count()


class CorruptionPerceptionsIndexSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CorruptionPerceptionsIndex
        exclude = ['created', 'id', 'modified']


class WorldEconomicOutlookSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.WorldEconomicOutlook
        exclude = ['created', 'id', 'modified']


class InternetUsageSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.InternetUsage
        exclude = ['created', 'id', 'modified']


class ConsumerPriceIndexSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ConsumerPriceIndex
        exclude = ['created', 'id', 'modified']


class GDPPerCapitalSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.GDPPerCapita
        exclude = ['created', 'id', 'modified']


class SuggestedCountrySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country__name')
    country_iso2 = serializers.CharField(source='country__iso2')
    region = serializers.CharField(source='country__region')

    class Meta:
        model = models.SuggestedCountry
        fields = ('hs_code', 'country_name', 'country_iso2', 'region')
