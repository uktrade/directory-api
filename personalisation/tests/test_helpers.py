import json
import pytest

from unittest.mock import Mock, patch

from personalisation import helpers


@pytest.mark.parametrize(
    'page,prev_pages,next_pages,show_first_page,\
show_last_page,first_item_number,last_item_number', (
        (2, [1], [3, 4, 5], False, True, 11, 20),
        (9, [6, 7, 8], [10], True, False, 81, 90),
    )
)
def test_parse_results(page, prev_pages,
                       next_pages, show_first_page,
                       show_last_page, first_item_number,
                       last_item_number):
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
            'total': 100,
            'max_score': 0.2876821,
            'hits': [{
                '_index': 'objects__feed_id_first_feed__date_2019',
                '_type': '_doc',
                '_id': 'dit:exportOpportunities:Opportunity:2',
                '_score': 0.2876821,
                '_source': {
                    'type': ['Document', 'dit:Opportunity'],
                    'title': 'France - Data analysis services',
                    'content':
                    'The purpose of this contract is to analyze...',
                    'url': 'www.great.gov.uk/opportunities/1'
                }
            }, {
                '_index': 'objects__feed_id_first_feed__date_2019',
                '_type': '_doc',
                '_id': 'dit:exportOpportunities:Opportunity:2',
                '_score': 0.18232156,
                '_source': {
                    'type': ['Document', 'dit:Opportunity'],
                    'title': 'Germany - snow clearing',
                    'content':
                    'Winter services for the properties1) Former...',
                    'url': 'www.great.gov.uk/opportunities/2'
                }
            }]
        }
    })
    response = Mock(status=200, content=mock_results)
    assert helpers.parse_results(response, "services", page) == {
       'results': [{
            'type': 'Export opportunity',
            'title': 'France - Data analysis services',
            'content': 'The purpose of this contract is to analyze...',
            'url': 'www.great.gov.uk/opportunities/1'
        },
        {
            'type': 'Export opportunity',
            'title': 'Germany - snow clearing',
            'content': 'Winter services for the properties1) Former...',
            'url': 'www.great.gov.uk/opportunities/2'
        }],
       'total_results': 100,
       'total_pages': 10,
       'previous_page': page-1,
       'next_page': page+1,
       'prev_pages': prev_pages,
       'next_pages': next_pages,
       'show_first_page': show_first_page,
       'show_last_page': show_last_page,
       'first_item_number': first_item_number,
       'last_item_number': last_item_number
    }


@pytest.mark.parametrize(
    'page,prev_pages,next_pages,show_first_page,\
show_last_page,first_item_number,last_item_number', (
        (1, [], [], False, False, 1, 0),
    )
)
def test_parse_results_error(page, prev_pages,
                             next_pages, show_first_page,
                             show_last_page, first_item_number,
                             last_item_number):
    mock_results = json.dumps({'error': 'Incorrect alias used'})
    response = Mock(status=200, content=mock_results)
    assert helpers.parse_results(response, 'services', page) == {
        'results': [],
        'total_results': 0,
        'total_pages': 1,
        'previous_page': page-1,
        'next_page': page+1,
        'prev_pages': prev_pages,
        'next_pages': next_pages,
        'show_first_page': show_first_page,
        'show_last_page': show_last_page,
        'first_item_number': first_item_number,
        'last_item_number': last_item_number
    }


def test_format_query():
    assert helpers.format_query('services', 2) == json.dumps({
        'query': {
            'bool': {
                'must': {
                    'bool': {
                        'should': [
                            {
                                'match': {
                                    'name': {
                                        'query': 'services',
                                        'minimum_should_match': '2<75%'
                                    }
                                }
                            },
                            {
                                'match': {
                                    'content': {
                                        'query': 'services',
                                        'minimum_should_match': '2<75%'
                                    }
                                }
                            },
                            {'match': {'keywords': 'services'}},
                            {'match': {'type': 'services'}}
                        ]
                    }
                },
                'should': [
                    {'match': {
                        'type': {
                            'query': 'Article',
                            'boost': 10000
                        }
                    }},
                    {'match': {
                        'type': {
                            'query': 'Market',
                            'boost': 10000
                        }
                    }},
                    {'match': {
                        'type': {
                            'query': 'Service',
                            'boost': 20000
                        }
                    }},
                    {'match': {
                        'type': {
                            'query': 'dit:Article',
                            'boost': 10000
                        }
                    }},
                    {'match': {
                        'type': {
                            'query': 'dit:Market',
                            'boost': 10000
                        }
                    }},
                    {'match': {
                        'type': {
                            'query': 'dit:Service',
                            'boost': 20000
                        }
                    }},
                    {'match': {
                        'type': {
                            'query': 'dit:aventri:Event',
                            'boost': 10000
                        }
                    }}
                ],
                'filter': [
                    {'terms': {
                        'type': [
                            'Article',
                            'Opportunity',
                            'Market',
                            'Service',
                            'dit:Article',
                            'dit:Opportunity',
                            'dit:Market',
                            'dit:Service',
                            'dit:aventri:Event'
                        ]
                    }}
                ]
            }
        },
        'from': 10,
        'size': 10
    })


# ExOps API

@patch('requests.get')
def test_exporting_is_great_handles_auth(mock_get, settings):
    client = helpers.ExportingIsGreatClient()
    client.base_url = 'http://b.co'
    client.secret = 123
    username = settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME
    password = settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD

    client.get_opportunities(2)

    mock_get.assert_called_once_with(
        'http://b.co/api/profile_dashboard',
        params={'sso_user_id': 2, 'shared_secret': 123},
        auth=helpers.exopps_client.auth
    )
    assert helpers.exopps_client.auth.username == username
    assert helpers.exopps_client.auth.password == password


