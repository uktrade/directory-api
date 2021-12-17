import sys
import time
from datetime import datetime, timedelta

import requests
from django.utils import timezone

from dataservices.models import ComtradeReport, ComtradeReportLoadblock, Country


class ComtradeLoader:
    """
    Loads or refreshes data from UN comtrade database.
    The loader requests import data for one country for one year in each request.
    The api it uses is throttled to one req/second and 100/hour so the idea is to run this loader each hour.
    the loader will stop after getting 5 successive errors.

    A control record is kept for each block so the loader knows where to continue from.
    It starts with all the countries for the previous year, then works backwards for 4 years.
    Once all blocks have been loaded, running the loader will do nothing until the load records age
    beyond a month - after which all the data are loaded again - adding any new rows and updating the
    trade values in existing ones.
    The loader blocks hold a report of the data loaded, the last time the loader ran that block.
    """

    maximum_successive_errors = 5
    previous_years_to_load = 5
    refresh_days = 10

    block_refresh_time = None
    iso_mapping = {}
    last_request = None

    def __init__(self):
        dataset = self.request_api(2019, 826, partner='ALL', direction='ALL', code='TOTAL')
        for row in dataset or []:
            self.iso_mapping[row.get('pt3ISO')] = row.get('ptCode')

    def write(self, txt, error=False):
        if error:
            sys.stdout.write(txt)
        else:
            sys.stdout.write(txt)

    def request_api(self, year, reporter, partner='0,826', direction=1, code='AG6'):
        url = 'https://comtrade.un.org/api/get'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
        }
        params = {
            'type': 'C',
            'freq': 'A',
            'px': 'HS',
            'ps': year,
            'r': reporter,
            'p': partner,  # Partner all or 0=world or partner id
            'rg': direction,  # 1-import, 2-export
            'cc': code,  # code length
        }
        # Wait until a second has elapsed since the end of the last request
        if self.last_request:
            while (datetime.now() - self.last_request).total_seconds() < 1:
                time.sleep(0.1)

        response = requests.get(url=url, headers=headers, params=params)
        self.last_request = datetime.now()
        if response.status_code == 200:
            return response.json().get('dataset')
        elif response.status_code == 409:
            self.write(f'Request blocked {response.status_code}', True)
            self.write(f'{response.text}', True)
        else:
            self.write(f'Bad response {response.status_code}', True)
            self.write(f'{response.text}', True)
        return

    def load_existing(self, year, country):
        out = {}
        for row in ComtradeReport.objects.filter(year=year, country=country):
            out[f'{row.commodity_code}:{row.uk_or_world}'] = row
        return out

    def map_iso_code(self, country):
        # Alters the requested iso code for the odd cases where comtrade has got it wrong
        return int(self.iso_mapping.get(country.iso3, country.iso1))

    def populate_from_bulk_request(self, country, year):

        self.write(f'{country.name} {year}')
        dataset = self.request_api(year=year, reporter=self.map_iso_code(country))
        if dataset is not None:
            create_block = []
            update_block = []
            existing = self.load_existing(year=year, country=country)
            for row in dataset:
                trade_value = row.get('TradeValue')
                classification = row.get('pfCode')
                commodity_code = row.get('cmdCode')
                uk_or_world = row.get('pt3ISO')
                # find the country
                ob = existing.get(f'{commodity_code}:{uk_or_world}')
                if not ob:
                    create_block.append(
                        ComtradeReport(
                            year=year,
                            classification=classification,
                            country_iso3=country.iso3,
                            uk_or_world=uk_or_world,
                            commodity_code=commodity_code,
                            country=country,
                            trade_value=trade_value,
                        )
                    )
                elif not ob.trade_value == trade_value:
                    ob.trade_value = trade_value
                    update_block.append(ob)
            ComtradeReport.objects.bulk_create(create_block)
            ComtradeReport.objects.bulk_update(update_block, ['trade_value'])
            result_str = f' \
                total: {len(dataset)}\n \
                created: {len(create_block)}\n \
                updated:{len(update_block)}\n \
                skipped:{len(dataset)-len(update_block)-len(create_block)}\n'
            self.write(result_str)
            return result_str, len(dataset)

        return None, None

    def process_year(self, year):
        error_count = 0
        for country in Country.objects.all():
            if country.iso1:
                blocks = ComtradeReportLoadblock.objects.filter(year=year, country=country, uk_or_world='WLD')
                block = (
                    blocks.first() if blocks else ComtradeReportLoadblock(year=year, country=country, uk_or_world='WLD')
                )

                created_updated = block.modified or block.created
                if block.row_count is None or (self.block_refresh_time and created_updated < self.block_refresh_time):
                    block.result, block.row_count = self.populate_from_bulk_request(country, year)
                    block.save()
                    error_count = 0 if block.result else error_count + 1
                    if error_count >= self.maximum_successive_errors:
                        self.write('Too many erors - shutting down')
                        return error_count
        return

    def process_all(self):
        self.block_refresh_time = timezone.now() - timedelta(days=self.refresh_days)
        this_year = int(datetime.now().strftime("%Y"))
        for year in range(this_year - 1, this_year - self.previous_years_to_load - 1, -1):
            if self.process_year(year):
                self.write('Loading still in progress', True)
                return
        self.write('Loading complete')
