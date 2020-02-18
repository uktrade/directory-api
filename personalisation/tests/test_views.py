import json

import requests

from unittest.mock import patch, Mock, call
from django.urls import reverse

from freezegun import freeze_time

from personalisation import views


def test_events_api(client, settings):
    """ We mock the call to ActivityStream """

    with patch('personalisation.helpers.search_with_activitystream') as search:
        mock_results = json.dumps({
            'took': 17,
            'timed_out': False,
            '_shards': {
                'total': 4,
                'successful': 4,
                'skipped': 0,
                'failed': 0
            },
            'hits': {
                'total': 5,
                'max_score': 0.2876821,
                'hits': [{
                    '_index': 'objects__feed_id_first_feed__date_2019',
                    '_type': '_doc',
                    '_id': 'dit:aventri:Event:2',
                    '_score': 0.2876821,
                    '_source': {
                        'type': ['dit:aventri:Event'],
                        'title': 'France - Data analysis services',
                        'content':
                        'The purpose of this contract is to analyze...',
                        'url': 'www.great.gov.uk/opportunities/1'
                    }
                }, {
                    '_index': 'objects__feed_id_first_feed__date_2019',
                    '_type': '_doc',
                    '_id': 'dit:aventri:Event:2',
                    '_score': 0.18232156,
                    '_source': {
                        'type': ['dit:aventri:Event'],
                        'title': 'Germany - snow clearing',
                        'content':
                        'Winter services for the properties1) Former...',
                        'url': 'www.great.gov.uk/opportunities/2'
                    }
                }]
            }
        })
        search.return_value = Mock(status_code=200, content=mock_results)

        response = client.get(reverse('personalisation-events'), data={'lat': '0', 'lng': '0'})
        context = response.context_data

        assert response.status_code == 200
        assert response.data == { 'results': [
                {
                  'type': 'Event',
                  'title': 'France - Data analysis services',
                  'content': 'The purpose of this contract is to analyze...',
                  'url': 'www.great.gov.uk/opportunities/1'
                },
                {
                  'type': 'Event',
                  'title': 'Germany - snow clearing',
                  'content': 'Winter services for the properties1) Former...',
                  'url': 'www.great.gov.uk/opportunities/2'
                }
            ]
        }

        """ What if there are no results? """
        search.return_value = Mock(
            status_code=200,
            content=json.dumps({
                'took': 17,
                'timed_out': False,
                '_shards': {
                    'total': 4,
                    'successful': 4,
                    'skipped': 0,
                    'failed': 0
                },
                'hits': {
                    'total': 0,
                    'hits': []
                }
            })
        )

        response = client.get(reverse('personalisation-events'), data={'sso_id': '123', 'lat': '0', 'lng': '0'})
        context = response.context_data

        assert response.status_code == 200
        assert response.data == { 'results': [] }

        """ What if ActivitySteam sends an error? """
        search.return_value = Mock(status_code=500,
                                   content="[service overloaded]")

        response = client.get(reverse('personalisation-events'), data={'sso_id': '123','lat': '0', 'lng': '0'})
        context = response.context_data

        assert response.status_code == 500
        # This can be handled on the front end as we wish
        assert response.data == { 'error_message': "[service overloaded]" }

        """ What if ActivitySteam is down? """
        search.side_effect = requests.exceptions.ConnectionError

        response = client.get(reverse('personalisation-events'), data={'sso_id': '123','lat': '0', 'lng': '0'})
        context = response.context_data

        assert response.status_code == 500
        # This can be handled on the front end as we wish
        assert response.data == { 'error_message': "Activity Stream connection failed" }

# Export Opportunities

def test_export_opportunities_api(client, settings):
    with patch('personalisation.helpers.get_opportunities') as get_opportunities:
        mock_results = {
            'relevant_opportunities': [{
              'title': 'French sardines required',
              'opportunity_url': 'www.example.com/export-opportunities/opportunities/french-sardines-required',
              'description': 'Nam dolor nostrum distinctio.Et quod itaque.',
              'submitted_on': '14 Jan 2020 15:26:45',
              'expiration_date': 'Sat, 06 Jun 2020',
            }]
        }
        get_opportunities.return_value = { 'status': 200, 'data': mock_results }

        response = client.get(reverse('personalisation-export-opportunities'), data={'sso_id': '123'})
        assert response.status_code == 200
        assert response.data == { 'results': [{
            'title': 'French sardines required',
            'opportunity_url': 'www.example.com/export-opportunities/opportunities/french-sardines-required',
            'description': 'Nam dolor nostrum distinctio.Et quod itaque.',
            'submitted_on': '14 Jan 2020 15:26:45',
            'expiration_date': 'Sat, 06 Jun 2020',
        }]}

