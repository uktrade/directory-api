from directory_constants.constants import lead_generation

from django.conf import settings


def get_ita_email(campaign, country):
    constants = lead_generation
    campaign_email_map = {
        constants.FOOD_IS_GREAT: {
            constants.FRANCE: settings.ITA_EMAILS_FOOD_IS_GREAT_FRANCE,
            constants.SINGAPORE: settings.ITA_EMAILS_FOOD_IS_GREAT_SINGAPORE,
        },
        constants.LEGAL_IS_GREAT: {
            constants.FRANCE: settings.ITA_EMAILS_LEGAL_IS_GREAT_FRANCE,
            constants.SINGAPORE: settings.ITA_EMAILS_LEGAL_IS_GREAT_SINGAPORE,
        }
    }
    return campaign_email_map[campaign][country]
