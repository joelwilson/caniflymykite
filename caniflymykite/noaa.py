import xml.etree.cElementTree as ET
from datetime import datetime

from collections import defaultdict
from datetime import datetime

import requests


URL = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php'
NOAA_ELEMENTS = ['temp', 'qpf', 'snow', 'pop12', 'sky', 'wdir', 'wspd', 'wgust']
XML_WEATHER_MAP = {
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


class Weather(object):
    '''Container class for storing and retrieving weather data.
    Input is the XML response text retrieved from an NOAA query. Weather 
    elements are accessed by name using the val() function.
    '''
    def __init__(self, xml):
        if isvalid(xml):
            parsed = parse_xml(xml)
        else:
            return None
        self.latlon = (parsed['latitude'], parsed['longitude'])
        self.times = parsed['times']
        self.weather = parsed['weather']
    
    def val(self, element, when=datetime.utcnow()):
        '''Given a weather element type and optional datetime object,
        returns the weather value closest to when.'''
        times = self.times[self.weather[element]['time-layout']]
        closest = min(times, key=lambda t: (when - t).total_seconds())
        index = times.index(closest)
        print element, self.weather[element]['values'][index], closest
        return self.weather[element]['values'][index]


def get_weather(zip, elems=NOAA_ELEMENTS):
    '''Returns weather data for a zip code as an instance of a weather
    data class.'''
    if not elems:
        elems = ['maxt', 'qpf', 'snow', 'pop12', 'sky', 
                'wdir', 'wspd', 'wgust']
    xml = query_noaa(zip, elems)
    return Weather(xml)


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
            r['times'][key].append(datetime.strptime(n.text[0:19], 
                '%Y-%m-%dT%H:%M:%S'))
    # weather parameters
    for p in root.findall('./data/parameters/*'):
        key = XML_WEATHER_MAP[(p.tag, p.get('type'))]
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
    
#print test_suite()