from rest_framework import serializers

from dataservices import models


class EaseOfDoingBusinessSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    class Meta:
        model = models.EaseOfDoingBusiness
        exclude = ['created', 'id', 'modified']

    def get_total(self, obj):
        return models.EaseOfDoingBusiness.objects.all().count()

    def get_country(self, obj):
        if obj.country:
            return obj.country.name

    def get_year(self, obj):
        # The year is implicit and should be updated when new data are imported
        return '2019'


class CorruptionPerceptionsIndexSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    class Meta:
        model = models.CorruptionPerceptionsIndex
        exclude = ['created', 'id', 'modified']

    def get_total(self, obj):
        return models.CorruptionPerceptionsIndex.objects.all().count()

    def get_country(self, obj):
        if obj.country:
            return obj.country.name

    def get_year(self, obj):
        # The year is implicit and should be updated when new data are imported
        return '2019'


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


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Income
        exclude = ['created', 'id', 'modified']


class RuleOfLawSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RuleOfLaw
        exclude = ['created', 'id', 'modified', 'country']


class SuggestedCountrySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country__name')
    country_iso2 = serializers.CharField(source='country__iso2')
    region = serializers.CharField(source='country__region')

    class Meta:
        model = models.SuggestedCountry
        fields = ('hs_code', 'country_name', 'country_iso2', 'region')
