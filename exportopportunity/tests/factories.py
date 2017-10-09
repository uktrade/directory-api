import factory

from directory_constants.constants import choices

from exportopportunity import models


def flatten_choices(choices):
    return [i[0] for i in choices]


def flatten_choices_array(choices):
    return [[i[0]] for i in choices]


class ExportOpportunityBaseactory(factory.django.DjangoModelFactory):

    full_name = factory.fuzzy.FuzzyText(length=1000)
    job_title = factory.fuzzy.FuzzyText(length=1000)
    email_address = 'test@example.com'
    company_name = factory.fuzzy.FuzzyText(length=1000)
    company_website = 'http://www.example.com'
    phone_number = factory.fuzzy.FuzzyText(length=30)
    contact_preference = factory.fuzzy.FuzzyChoice(
        flatten_choices_array(choices.CONTACT_OPTIONS)
    )
    campaign = factory.fuzzy.FuzzyText(length=100)
    country = factory.fuzzy.FuzzyText(length=100)


class ExportOpportunityFoodFactory(ExportOpportunityBaseactory):
    class Meta:
        model = models.ExportOpportunityFood

    business_model = factory.fuzzy.FuzzyChoice(
        flatten_choices_array(choices.FOOD_LEAD_GENERATION_BUSINESS_MODELS)
    )
    target_sectors = factory.fuzzy.FuzzyChoice(
        flatten_choices_array(choices.FOOD_LEAD_GENERATION_SECTORS)
    )
    products = factory.fuzzy.FuzzyChoice(
        flatten_choices_array(choices.FOOD_LEAD_GENERATION_PRODUCT_TYPES)
    )
    order_size = factory.fuzzy.FuzzyChoice(
        flatten_choices(choices.ORDER_SIZE_OPTIONS)
    )
    order_deadline = factory.fuzzy.FuzzyChoice(
        flatten_choices(choices.ORDER_DEADLINE_OPTIONS)
    )
    additional_requirements = factory.fuzzy.FuzzyText(length=100)
    business_model_other = factory.fuzzy.FuzzyText(length=30)
    target_sectors_other = factory.fuzzy.FuzzyText(length=30)
    products_other = factory.fuzzy.FuzzyText(length=30)


class ExportOpportunityLegalFactory(ExportOpportunityBaseactory):
    class Meta:
        model = models.ExportOpportunityLegal

    advice_type = factory.fuzzy.FuzzyChoice(
        flatten_choices_array(choices.LEGAL_LEAD_GENERATION_NEED)
    )
    advice_type_other = factory.fuzzy.FuzzyText(length=30)
    target_sectors = factory.fuzzy.FuzzyChoice(
        flatten_choices_array(choices.LEGAL_LEAD_GENERATION_SECTORS)
    )
    target_sectors_other = factory.fuzzy.FuzzyText(length=30)
    additional_requirements = factory.fuzzy.FuzzyText(length=100)
    order_deadline = factory.fuzzy.FuzzyChoice(
        flatten_choices(choices.ORDER_DEADLINE_OPTIONS)
    )
