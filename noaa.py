from datetime import datetime

import requests


URL = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php'
W_ELEMENTS = ['maxt', 'qpf', 'snow', 'pop12', 'sky', 'wdir', 'wspd', 'wgust']


class Weather(dict):
    pass


def get_weather(zip, elems=W_ELEMENTS):
    '''Returns weather data for a zip code as an instance of a weather
    data class.'''
    
    if not elems:
        elems = ['maxt', 'qpf', 'snow', 'pop12', 'sky', 
                'wdir', 'wspd', 'wgust']

    xml = query_noaa(zip, elems)
    return parse_xml(xml) if isvalid(xml)


def query_noaa(zip, elems, url=URL):
    params = {
        'zipCodeList': zip,
        'product': 'time-series'
    }
    params.update((e, e) for e in elems)
    r = requests.get(URL, params=params)
    return r.text if r.ok else None


def mph(knots):
    '''Converts knots to MPH. Returns a float respresenting MPH'''
    return round(knots * 1.15078, 2)


def test_suite():
    assert mph(7) == 8.06
    assert mph(14) == 16.11
    assert isinstance(query_noaa(90210, ['sky', 'maxt']), basestring)
    assert isinstance(get_weather(90210), Weather)
    return 'tests pass!'
    
print test_suite()