import markdown2
from functools import partial
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from urllib3.util import parse_url

from django.utils.text import Truncator

from directory_constants import urls

build_events_url = partial(urljoin, urls.domestic.EVENTS)


def parse_search_results(content):

    def strip_html(result):
        content = result.get('content', '')
        html = markdown2.markdown(content)
        result['content'] = ''.join(
            BeautifulSoup(html, "html.parser").findAll(text=True)
        ).rstrip()

    def format_events_url(result):
        if "dit:aventri:Event" in result['type']:
            url = parse_url(result['url'])
            result['url'] = build_events_url(url.request_uri)

    def abridge_long_contents(result):
        if 'content' in result:
            result['content'] = Truncator(result['content']).chars(160)

    def format_display_type(result):
        mappings = {
            'dit:aventri:Event': 'Event',
            'dit:Opportunity': 'Export opportunity',
            'Opportunity': 'Export opportunity',
            'Market': 'Online marketplace',
            'dit:Market': 'Online marketplace',
            'Article': 'Article',
            'dit:Article': 'Article',
            'Service': 'Service',
            'dit:Service': 'Service'
        }
        for value, replacement in mappings.items():
            if value in result['type']:
                result['type'] = replacement

    results = [hit['_source'] for hit in content['hits']['hits']]

    # This removes HTML tags and markdown received from CMS results
    #
    # It first line converts the markdown received into HTML
    # Then we remove HTML tags
    # It also removes unneccessary \n added by the markdown library
    for result in results:
        strip_html(result)
        format_events_url(result)
        format_display_type(result)
        abridge_long_contents(result)

    return results
