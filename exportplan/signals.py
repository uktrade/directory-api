from dataservices import helpers


def add_target_markets_data(sender, instance, *args, **kwargs):
    existing_countries = []
    if not instance._state.adding:
        pre_save_instance = sender.objects.get(pk=instance.pk)
        existing_countries = [market['country'] for market in pre_save_instance.target_markets]

    for country in [market['country'] for market in instance.target_markets]:
        if country not in existing_countries:
            index = next((index for (index, d) in enumerate(instance.target_markets) if d["country"] == country), None)
            # for now we are supporting ok one commodity
            commodity_code = instance.export_commodity_codes[0]
            rules_regulations = helpers.MADB().get_rules_and_regulations(commodity_code)
            # Get all market data from dataservices and store again instance
            instance.target_markets[index]['export_duty'] = rules_regulations['export_duty']
            instance.target_markets[index]['easeofdoingbusiness'] = helpers.get_ease_of_business_index(
                rules_regulations['country_code']
            )
            instance.target_markets[index]['corruption_perceptions_index'] = helpers.get_corruption_perception_index(
                rules_regulations['country_code']
            )
            instance.target_markets[index]['last_year_data'] = helpers.get_last_year_import_data(
                rules_regulations['country_code'], commodity_code
            )
