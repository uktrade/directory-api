import io
import requests

import xmltodict
from zipfile import ZipFile


def flatten_ordered_dict(d):
    # flatten rows of ordered  dict so can be accessed as key\values
    out = {}
    for row in d:
        out[row['@name']] = (row.get('@key'), row.get('#text'))
    return out


def from_url_get_xml(url):
    response = requests.get(url)
    with ZipFile(io.BytesIO(response.content)) as myzip:
        # Assumption is that the first file is the data file we want extract
        filename = myzip.namelist()[0]
        with myzip.open(filename) as myfile:
            xml = myfile.read()
    return xmltodict.parse(xml)