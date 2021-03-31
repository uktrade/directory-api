import json

from django.conf import settings


class Metadata:
    """
    Wrapper around the raw metadata with helper functions
    """

    def __init__(self, data):
        self.data = data

    def get_trading_bloc_list(self):
        return self.data["trading_blocs"]

    def get_admin_area(self, admin_area_id):
        for admin_area in self.data["country_admin_areas"]:
            if admin_area["id"] == admin_area_id and admin_area["disabled_on"] is None:
                return admin_area

    def get_admin_areas(self, admin_area_ids):
        """
        Helper to get admin areas data in bulk.

        :param admin_area_ids: either a list or a comma separated string of UUIDs
        :return: GENERATOR - data of admin areas
        """
        area_ids = admin_area_ids or []
        if type(area_ids) == str:
            area_ids = admin_area_ids.replace(" ", "").split(",")
        admin_areas = [self.get_admin_area(area_id) for area_id in area_ids]
        return admin_areas

    def get_admin_areas_by_country(self, country_id):
        return [
            admin_area for admin_area in self.data["country_admin_areas"] if admin_area["country"]["id"] == country_id
        ]

    def get_country(self, country_id):
        for country in self.data["countries"]:
            if country["id"] == country_id:
                return country

    def get_country_list(self):
        return self.data["countries"]

    def get_sector(self, sector_id):
        for sector in self.data.get("sectors", []):
            if sector["id"] == sector_id:
                return sector

    def get_sectors(self, sector_ids):
        """
        Helper to get sectors data in bulk.

        :param sector_ids: either a list or a comma separated string of UUIDs
        :return: GENERATOR - data of sectors
        """
        sec_ids = sector_ids or []
        if type(sec_ids) == str:
            sec_ids = sector_ids.replace(" ", "").split(",")
        sectors = (self.get_sector(sector_id) for sector_id in sec_ids)
        return sectors

    def get_sector_list(self, level=None):
        return [
            sector
            for sector in self.data["sectors"]
            if (level is None or sector["level"] == level) and sector["disabled_on"] is None
        ]


def get_metadata():
    file = f"{settings.ROOT_DIR}/directory-api/dataservices/resources/metadata.json"
    with open(file) as f:
        return Metadata(json.load(f))


metadata = get_metadata()
