from django.db.models import Max
from rest_framework import serializers

from dataservices import models


class EaseOfDoingBusinessSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    max_rank = serializers.SerializerMethodField()

    class Meta:
        model = models.EaseOfDoingBusiness
        exclude = ['created', 'id', 'modified', 'country']

    def get_max_rank(self, obj):
        agg = models.EaseOfDoingBusiness.objects.aggregate(Max('value'))
        for key in agg:
            return agg[key]

    def get_total(self, obj):
        return models.EaseOfDoingBusiness.objects.filter(year=obj.year).count()

    def get_rank(self, obj):
        return obj.value


class CorruptionPerceptionsIndexSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = models.CorruptionPerceptionsIndex
        exclude = ['created', 'id', 'modified', 'country', 'country_name', 'country_code']

    def get_total(self, obj):
        return models.CorruptionPerceptionsIndex.objects.filter(year=obj.year).count()


class WorldEconomicOutlookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorldEconomicOutlook
        exclude = ['created', 'id', 'modified']


class InternetUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InternetUsage
        exclude = ['created', 'id', 'modified', 'country']


class ConsumerPriceIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ConsumerPriceIndex
        exclude = ['created', 'id', 'modified', 'country']


class GDPPerCapitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GDPPerCapita
        exclude = ['created', 'id', 'modified']


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Income
        exclude = ['created', 'id', 'modified', 'country']


class RuleOfLawSerializer(serializers.ModelSerializer):
    year = serializers.SerializerMethodField()

    class Meta:
        model = models.RuleOfLaw
        exclude = ['created', 'id', 'modified', 'country']

    def get_year(self, obj):
        # The year is implicit and should be updated when new data are imported
        return '2020'


class SuggestedCountrySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country__name')
    country_iso2 = serializers.CharField(source='country__iso2')
    region = serializers.CharField(source='country__region')

    class Meta:
        model = models.SuggestedCountry
        fields = ('hs_code', 'country_name', 'country_iso2', 'region')


class TradingBlocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TradingBlocs
        exclude = ['created', 'id', 'modified']


class ComtradeReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ComtradeReport
        exclude = ['id', 'country', 'country_iso3']


class PopulationUrbanRuralSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PopulationUrbanRural
        exclude = ['id', 'country']


class CIAFactbookSerializer(serializers.ModelSerializer):
    languages = serializers.SerializerMethodField()

    class Meta:
        model = models.CIAFactbook
        exclude = ['id', 'country', 'modified', 'factbook_data']

    def get_languages(self, obj):
        return (obj.factbook_data or {}).get('people', {}).get('languages', {})


class PopulationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PopulationData
        fields = [
            'year',
            'gender',
            '0-4',
            '5-9',
            '10-14',
            '15-19',
            '20-24',
            '25-29',
            '30-34',
            '35-39',
            '40-44',
            '45-49',
            '50-54',
            '55-59',
            '60-64',
            '65-69',
            '70-74',
            '75-79',
            '80-84',
            '85-89',
            '90-94',
            '95-99',
            '100+',
        ]
        extra_kwargs = {
            '0-4': {'source': 'age_0_4'},
            '5-9': {'source': 'age_5_9'},
            '10-14': {'source': 'age_10_14'},
            '15-19': {'source': 'age_15_19'},
            '20-24': {'source': 'age_20_24'},
            '25-29': {'source': 'age_25_29'},
            '30-34': {'source': 'age_30_34'},
            '35-39': {'source': 'age_35_39'},
            '40-44': {'source': 'age_40_44'},
            '45-49': {'source': 'age_45_49'},
            '50-54': {'source': 'age_50_54'},
            '55-59': {'source': 'age_55_59'},
            '60-64': {'source': 'age_60_64'},
            '65-69': {'source': 'age_65_69'},
            '70-74': {'source': 'age_70_74'},
            '75-79': {'source': 'age_75_79'},
            '80-84': {'source': 'age_80_84'},
            '85-89': {'source': 'age_85_89'},
            '90-94': {'source': 'age_90_94'},
            '95-99': {'source': 'age_95_99'},
            '100+': {'source': 'age_100_plus'},
        }


class CommodityExportsSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name')

    class Meta:
        model = models.CommodityExports
        exclude = ['id', 'modified', 'country', 'created']
