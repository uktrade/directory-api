import pytz
from datetime import datetime
from conf import settings

from dataservices import helpers
from exportplan import helpers as export_helpers


def add_target_markets_data(sender, instance, *args, **kwargs):
    pre_save_target_markets = []
    if not instance._state.adding:
        pre_save_instance = sender.objects.only('target_markets').get(pk=instance.pk)
        pre_save_target_markets = [market['country_name'] for market in pre_save_instance.target_markets]

    for target_market in instance.target_markets:
        country = target_market['country_name']
        if country in pre_save_target_markets:
            continue

        country_code = export_helpers.get_iso3_by_country_name(country)

        if len(instance.export_commodity_codes) > 0:
            commodity_code = instance.export_commodity_codes[0]['commodity_code']
            target_market['last_year_data'] = helpers.get_last_year_import_data(
                commodity_code=commodity_code, country=country
            )
            if settings.FEATURE_COMTRADE_HISTORICAL_DATA_ENABLED:
                target_market[
                    'historical_import_data'] = helpers.get_historical_import_data(
                    commodity_code=commodity_code, country=country
                )
        else:
            target_market['last_year_data'] = {}

        if country_code:
            timezone = export_helpers.get_timezone(country_code)
            target_market.update({
                'easeofdoingbusiness': helpers.get_ease_of_business_index(country_code),
                'corruption_perceptions_index': helpers.get_corruption_perception_index(country_code),
                'timezone': timezone,
                'utz_offset': datetime.now(pytz.timezone(timezone)).strftime('%z'),
                'world_economic_outlook_data': helpers.get_world_economic_outlook_data(country_code),
            })

        target_market['cia_factbook_data'] = helpers.get_cia_factbook_data(country_name=country, data_keys=[
            'languages', 'government', 'transportation', 'people'
        ])
