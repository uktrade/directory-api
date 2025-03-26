import csv
import json

from django.core.management import BaseCommand

from dataservices.models import Boundary, ChamberOfCommerce, ContactCard, GrowthHub, Place


def ingest_boundaries():
    with open('dataservices/resources/boundaries.csv', 'r', encoding='utf-8-sig') as f:
        boundaries = csv.DictReader(f)
        for boundary in boundaries:
            b = Boundary.objects.get_or_create(code=boundary['code'])
            b[0].name = boundary['name']
            b[0].type = boundary['level']
            b[0].save()


def ingest_growth_hubs_json():
    try:
        with open('dataservices/resources/growth-hubs.json') as f:
            growth_hubs = json.load(f)
    except Exception as e:
        raise FileNotFoundError(e)
    for hub in growth_hubs:
        cc = ContactCard.objects.get_or_create(
            website=hub['contacts']['website'],
        )
        cc[0].phone = hub['contacts']['phone']
        cc[0].email = hub['contacts']['email']
        cc[0].save()
        gh = GrowthHub.objects.get_or_create(name=hub['name'])
        gh[0].description = hub['description']
        gh[0].contacts = cc[0]
        gh[0].boundaries.clear()
        gh[0].save()
        if hub['coverage']:
            for boundary in hub['coverage']['boundaries']:
                gh[0].boundaries.add(Boundary.objects.get(code=boundary['code']))


def ingest_chambers_of_commerce():
    try:
        with open('dataservices/resources/commerce-chambers.json') as f:
            commerce_chambers = json.load(f)
    except Exception as e:
        raise FileNotFoundError(e)
    for chamber in commerce_chambers:
        cc = ContactCard.objects.get_or_create(
            website=chamber['contacts']['website'],
        )
        cc[0].phone = chamber['contacts']['phone']
        cc[0].email = chamber['contacts']['email']
        cc[0].save()
        place = Place.objects.get_or_create(
            address=chamber['place']['address'],
            postcode=chamber['place']['postcode'],
            latitude=chamber['place']['latitude'],
            longitude=chamber['place']['longitude'],
            northings=chamber['place']['northings'],
            eastings=chamber['place']['eastings'],
        )
        coc = ChamberOfCommerce.objects.get_or_create(name=chamber['name'], place=place[0])
        coc[0].contacts = cc[0]
        coc[0].save()


class Command(BaseCommand):
    # create boundaries and assign to growth hubs.
    def handle(self, *args, **options):
        ingest_boundaries()
        ingest_growth_hubs_json()
        ingest_chambers_of_commerce()
