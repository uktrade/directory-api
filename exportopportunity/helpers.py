from django.conf import settings


def get_ita_email(campaign, country):
    campaign_email_map = {
        'food-is-great': {
            'france': settings.ITA_EMAILS_FOOD_IS_GREAT_FRANCE,
            'singapore': settings.ITA_EMAILS_FOOD_IS_GREAT_SINGAPORE,
        }
    }
    return campaign_email_map[campaign][country]
