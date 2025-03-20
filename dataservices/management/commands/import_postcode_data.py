import csv
import json

from django.core.management import BaseCommand

from dataservices.models import Boundary, ChamberOfCommerce, ContactCard, GrowthHub, Place


def ingest_boundaries():
    with open('dataservices/resources/boundaries.csv', 'r', encoding='utf-8-sig') as f:
        boundaries = csv.DictReader(f)
        for boundary in boundaries:
            Boundary.objects.update_or_create(name=boundary['name'], code=boundary['code'], type=boundary['level'])


def ingest_growth_hubs_json():
    try:
        with open('dataservices/resources/growth-hubs.json') as f:
            growth_hubs = json.load(f)
    except Exception as e:
        raise FileNotFoundError(e)
    for hub in growth_hubs:
        cc = ContactCard.objects.get_or_create(
            website=hub['contacts']['website'], phone=hub['contacts']['phone'], email=hub['contacts']['email']
        )
        gh = GrowthHub.objects.get_or_create(name=hub['name'], description=hub['description'], contacts=cc[0])
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
            phone=chamber['contacts']['phone'],
            email=chamber['contacts']['email'],
        )
        place = Place.objects.get_or_create(
            address=chamber['place']['address'],
            postcode=chamber['place']['postcode'],
            latitude=chamber['place']['latitude'],
            longitude=chamber['place']['longitude'],
            northings=chamber['place']['northings'],
            eastings=chamber['place']['eastings'],
        )
        ChamberOfCommerce.objects.update_or_create(name=chamber['name'], contacts=cc[0], place=place[0])


class Command(BaseCommand):
    # create boundaries and assign to growth hubs.
    def handle(self, *args, **options):
        ingest_boundaries()
        ingest_growth_hubs_json()
        ingest_chambers_of_commerce()
