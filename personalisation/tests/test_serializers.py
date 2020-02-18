from personalisation import serializers


def test_parse_search_results():
    content = {
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
                    'The purpose of this contract is to analyze Python\
 For Loops. A for loop is used for iterating over a sequence (that is\
  either a list, a tuple, a dictionary, a set, or a string). This is \
  less like the for keyword in other programming language, and works \
  more like an iterator method as found in other object-orientated \
  programming languages.',
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
                    'Winter services for the properties1) Former…',
                    'url': 'www.great.gov.uk/opportunities/2'
                }
            }, {
                '_index': 'objects__feed_id_first_feed__date_2019',
                '_type': '_doc',
                '_id': 'dit:exportOpportunities:Opportunity:3',
                '_score': 0.18232156,
                '_source': {
                    'type': ['Document', 'dit:Article'],
                    'title': 'Test Shortening Content',
                    'content':
                    "The UK and the EU have agreed a draft agreement\
 on withdrawing from the EU. Read the [Prime Minister's statement](ht\
tps://www.gov.k/government/speeches/pms-statement-on-brexit-14-novembe\
r-2018) and the full",
                    'url': 'www.great.gov.uk/opportunities/3'
                }
            }, {
                '_index': 'objects__feed_id_first_feed__date_2019',
                '_type': '_doc',
                '_id': 'dit:exportOpportunities:Opportunity:4',
                '_score': 0.18232156,
                '_source': {
                    'type': ['Document', 'dit:Article'],
                    'title': 'Test No Content',
                    'url': 'www.great.gov.uk/opportunities/4'
                }
            }, {
                '_index': 'objects__feed_id_first_feed__date_2019',
                '_type': '_doc',
                '_id': 'dit:exportOpportunities:Opportunity:5',
                '_score': 0.18232156,
                '_source': {
                    'type': ['Document', 'dit:Article'],
                    'title': 'Test No URL',
                    'content': 'Here is the content'
                }
            }, {
                '_index': 'objects__feed_id_first_feed__date_2019',
                '_type': '_doc',
                '_id': 'dit:exportOpportunities:Event:1',
                '_score': 0.18232156,
                '_source': {
                    'type': ['Document', 'dit:aventri:Event'],
                    'title': 'Test Event URL Parsing',
                    'content': 'Great event',
                    'url': 'https://eu.eventscloud.com\
/ehome/index.php?eventid=200188836&'
                }
            }]
        }
    }

    assert serializers.parse_search_results(content) == [{
        'type': 'Export opportunity',
        'title': 'France - Data analysis services',
        'content': 'The purpose of this contract is to analyze Python\
 For Loops. A for loop is used for iterating over a sequence (that is\
  either a list, a tuple, a dictionary, a…',
        'url': 'www.great.gov.uk/opportunities/1'
    }, {
        'type': 'Export opportunity',
        'title': 'Germany - snow clearing',
        'content': 'Winter services for the properties1) Former…',
        'url': 'www.great.gov.uk/opportunities/2'
    }, {
        'type': 'Article',
        'title': 'Test Shortening Content',
        'content': 'The UK and the EU have agreed a draft agreement\
 on withdrawing from the EU. Read the Prime Minister\'s statement and\
 the full',
        'url': 'www.great.gov.uk/opportunities/3'
    }, {
        'type': 'Article',
        'title': 'Test No Content',
        'url': 'www.great.gov.uk/opportunities/4',
        'content': ''
    }, {
        'type': 'Article',
        'title': 'Test No URL',
        'content': 'Here is the content',
    }, {
        'type': 'Event',
        'title': 'Test Event URL Parsing',
        'content': 'Great event',
        'url': 'https://www.events.great.gov.uk/\
ehome/index.php?eventid=200188836&'
    }]
