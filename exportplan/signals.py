import pytz
from datetime import datetime
from conf import settings

from dataservices import helpers
from exportplan import helpers as export_helpers


def add_target_markets_data(sender, instance, *args, **kwargs):
    pre_save_target_markets = []
    if not instance._state.adding:
        pre_save_instance = sender.objects.only('target_markets').get(pk=instance.pk)
        pre_save_target_markets = [market['country'] for market in pre_save_instance.target_markets]

    for target_market in instance.target_markets:
        country = target_market['country']
        if country in pre_save_target_markets:
            continue

        country_code = export_helpers.get_iso3_by_country_name(country)

        commodity_code = instance.export_commodity_codes[0]
        timezone = export_helpers.get_timezone(country_code)

        target_market.update({
            'easeofdoingbusiness': helpers.get_ease_of_business_index(
                country_code),
            'corruption_perceptions_index': helpers.get_corruption_perception_index(
                country_code),
            'last_year_data': helpers.get_last_year_import_data(
                commodity_code=commodity_code, country=country),
            'timezone': timezone,
            'utz_offset': datetime.now(pytz.timezone(timezone)).strftime('%z')
        })

        rules_regulations = helpers.MADB().get_rules_and_regulations(country)
        if rules_regulations:
            target_market['export_duty'] = rules_regulations['export_duty']
            target_market['commodity_name'] = rules_regulations['commodity_name']
        else:
            # No regulations found but lets set some blanks for unknown data
            target_market['export_duty'] = ''
            target_market['commodity_name'] = ''

        if settings.FEATURE_COMTRADE_HISTORICAL_DATA_ENABLED:
            target_market[
                'historical_import_data'] = helpers.get_historical_import_data(
                commodity_code=commodity_code, country=country
            )
