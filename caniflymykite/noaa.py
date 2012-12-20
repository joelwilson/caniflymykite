import xml.etree.cElementTree as ET

from collections import defaultdict
from datetime import datetime

import requests


URL = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php'
W_ELEMENTS = ['temp', 'qpf', 'snow', 'pop12', 'sky', 'wdir', 'wspd', 'wgust']
WEATHER_DESC = {
    ('precipitation', 'liquid'):                    'rain',
    ('precipitation', 'snow'):                      'snow',
    ('wind-speed', 'gust'):                         'wind_gust',
    ('wind-speed', 'sustained'):                    'wind_speed',
    ('direction', 'wind'):                          'wind_dir',
    ('cloud-amount', 'total'):                      'cloud_amount',
    ('temperature', 'hourly'):                      'temperature',
    ('probability-of-precipitation', '12 hour'):    'rain_prob',
    ('weather', None):                              'weather'
}


def get_weather(zip, elems=W_ELEMENTS):
    '''Returns weather data for a zip code as an instance of a weather
    data class.'''
    if not elems:
        elems = ['maxt', 'qpf', 'snow', 'pop12', 'sky', 
                'wdir', 'wspd', 'wgust']
    xml = query_noaa(zip, elems)
    return parse_xml(xml) if isvalid(xml) else None


def query_noaa(zip, elems, url=URL):
    params = {
        'zipCodeList': zip,
        'product': 'time-series'
    }
    params.update((e, e) for e in elems)
    r = requests.get(URL, params=params)
    return r.text if r.ok else None

    
def parse_xml(xml):
    '''Parses the XML structure. Returns dict of weather, time series,
    latitude, and longitude values and attributes. Works with the results 
    from a single point only.
    '''
    r = {'times': {}, 'weather': {}}
    root = ET.fromstring(xml)
    # lat & lon
    r.update(i for p in root.findall('./data/location/point') 
             for i in p.items())
    # times by layout-key
    for n in root.findall('./data/time-layout/'):
        if n.tag == 'layout-key':
            key = n.text
            r['times'][key] = []
        if n.tag == 'start-valid-time':
            r['times'][key].append(n.text[0:19])
    # weather parameters
    for p in root.findall('./data/parameters/*'):
        key = WEATHER_DESC[(p.tag, p.get('type'))]
        r['weather'][key] = defaultdict(list)
        r['weather'][key]['time-layout'] = (p.get('time-layout'))
        for v in p.findall('./value'):
            r['weather'][key]['values'].append(v.text)
    return r
    

def isvalid(xml):
    '''Returns True if the xml response contains no NOAA error message.'''
    errors = ['<h2>ERROR</h2>', '<errorMessage>', '<error>']
    for e in errors: 
        if e in xml:
            return False
    return True
    

def mph(knots, precision=2):
    '''Converts knots to MPH.'''
    return round(int(knots) * 1.15078, precision)


def test_suite():
    assert mph(7) == 8.06
    assert mph(14) == 16.11
    assert True == isvalid(query_noaa(90210, ['sky']))
    assert True == isvalid(query_noaa(95382, ['sky', 'snow']))
    assert False == isvalid(query_noaa(9021, ['sky']))
    assert False == isvalid(query_noaa(902101, ['sky']))
    assert not get_weather(911111)
    assert get_weather(90210)
    return 'tests pass!'
    
print test_suite()