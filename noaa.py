import xml.etree.cElementTree as ET
from datetime import datetime

from collections import defaultdict
from datetime import datetime

import requests


__all__ = ['Weather', 'get_weather', 'query_noaa', 'WeatherError',
           'parse_xml', 'isvalid', 'tomph', 'NOAA_ELEMS', 'heading']
URL = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php'
NOAA_ELEMS = ['temp', 'qpf', 'snow', 'pop12', 'sky', 'wdir', 'wspd', 'wgust']
XML_WEATHER_MAP = {
    ('precipitation', 'liquid'):                    'rain',
    ('precipitation', 'snow'):                      'snow',
    ('wind-speed', 'gust'):                         'wind_gust',
    ('wind-speed', 'sustained'):                    'wind_speed',
    ('direction', 'wind'):                          'wind_dir',
    ('cloud-amount', 'total'):                      'cloud_amount',
    ('temperature', 'hourly'):                      'temperature',
    ('temperature', 'maximum'):                     'max_temp',
    ('temperature', 'minimum'):                     'min_temp',
    ('probability-of-precipitation', '12 hour'):    'rain_prob',
    ('weather', None):                              'weather'
}


class WeatherError(Exception):
    pass


class Weather(object):
    '''Container class for storing and retrieving weather data.
    Input is the XML response text retrieved from an NOAA query. Weather 
    elements are accessed by name using the val() function.
    '''
    def __init__(self, xml):
        if not isvalid(xml):
            raise WeatherError, 'Invalid XML data: \n{0}'.format(xml)
        else:
            parsed = parse_xml(xml)
        self.latlon = (parsed['latitude'], parsed['longitude'])
        self.times = parsed['times']
        self.weather = parsed['weather']
    
    def val(self, element, when=datetime.utcnow()):
        '''Given a weather element type and optional datetime object,
        returns the weather value closest to when.'''
        times = self.times[self.weather[element]['time-layout']]
        closest = min(times, key=lambda t: abs((when - t)).total_seconds())
        index = times.index(closest)
        return self.weather[element]['values'][index]
        
    def __repr__(self):
        items = {
            'name': self.__class__.__name__,
            'latlon': self.latlon, 
            'times': self.times.keys(),
            'wx': self.weather.keys()
        }
        return "{name}({latlon}, {times}, {wx})".format(**items)


def get_weather(zip, elems=NOAA_ELEMS):
    '''Returns weather data for a zip code as an instance of a weather
    data class.'''
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
    '''Returns True if the xml response is NOAA valid.'''
    errors = ['<h2>ERROR</h2>', '<errorMessage>', '<error>']
    for e in errors: 
        if e in xml:
            return False
    if 'http://www.w3.org/' not in xml:
        return False
    return True
    

def tomph(knots, precision=2):
    '''Converts knots to MPH.'''
    return round(float(knots) * 1.15078, precision)

    
def heading(degrees):
    '''Returns a string representation of an integer direction in degrees.
    
    Examples:
        heading(360) => "N"
        heading(45)  => "NE"
    '''
    pass