import xml.etree.cElementTree as ET
import random as rand
from datetime import datetime
from collections import defaultdict

import requests

import utils


__all__ = ['query_noaa', 'ForecastError', 'parse_forecast_xml',
           'isvalid', 'NOAA_ELEMS', 'canfly', 'forecast', 'Forecast']
URL = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php'
NOAA_ELEMS = ('temp', 'qpf', 'snow', 'pop12', 'sky', 'wdir', 'wspd', 'wgust')
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


class ForecastError(Exception):
    '''Basic exception class for exceptions in the Forecast class.'''
    pass


class Forecast(object):
    '''Container class for storing and retrieving weather data.
    Input is the XML response text retrieved from an NOAA query. Weather
    elements are accessed by name using the val() function.
    '''
    def __init__(self, noaa_xml):
        if not isvalid(noaa_xml):
            raise ForecastError('Invalid XML data: \n{0}'.format(noaa_xml))
        else:
            parsed = parse_forecast_xml(noaa_xml)
        self.latlon = (float(parsed['latitude']), 
                       float(parsed['longitude']))
        self.times = parsed['times']
        self.weather = parsed['weather']

    def get(self, element, when=datetime.now(), debug=False):
        '''Given a weather element type and optional datetime object,
        returns the weather value closest to when.'''
        times = self.times[self.weather[element]['time-layout']]
        closest = min(times, key=lambda t: abs((when - t)).total_seconds())
        index = times.index(closest)
        if debug:
            print 'Element: ', element, '\n', \
                   zip(times, self.weather[element]['values']), '\n', \
                   closest, '\n', \
                   self.weather[element]['values'][index], '\n'
        return self.weather[element]['values'][index]

    def __repr__(self):
        items = {
            'name': self.__class__.__name__,
            'latlon': self.latlon,
            'times': self.times.keys(),
            'wx': self.weather.keys()
        }
        return '{name}({latlon}, {times}, {wx})'.format(**items)


def forecast(lat, lon, elems=NOAA_ELEMS):
    '''Return a Forecast object containing weather forecast for the given
    latitude and longitude.'''
    xml = query_noaa(lat, lon, elems)
    return Forecast(xml)


def query_noaa(lat, lon, elems, url=URL):
    '''Returns the XML returned by a query to NOAA with the passed
    lat, lon and list or tuple of weather elements.'''
    params = {
        'lat': lat,
        'lon': lon,
        'product': 'time-series'
    }
    params.update((elem, elem) for elem in elems)
    r = requests.get(url, params=params)
    return r.text if r.ok else None


def parse_forecast_xml(xml):
    '''Parses the XML structure. Returns dict of weather, time series,
    latitude, and longitude values and attributes. Works with the results
    from a single point only.
    '''
    results = {'times': {}, 'weather': {}}
    root = ET.fromstring(xml)
    # lat & lon
    results.update(i for points in root.findall('./data/location/point')
                   for i in points.items())
    # times by layout-key
    for node in root.findall('./data/time-layout/'):
        if node.tag == 'layout-key':
            key = node.text
            results['times'][key] = []
        if node.tag == 'start-valid-time':
            results['times'][key].append(datetime.strptime(node.text[0:19],
                '%Y-%m-%dT%H:%M:%S'))
    # weather parameters
    for param in root.findall('./data/parameters/*'):
        key = XML_WEATHER_MAP[(param.tag, param.get('type'))]
        results['weather'][key] = defaultdict(list)
        results['weather'][key]['time-layout'] = (param.get('time-layout'))
        for value in param.findall('./value'):
            results['weather'][key]['values'].append(value.text)
    return results


def isvalid(xml):
    '''Returns True if the xml response is NOAA valid.'''
    errors = ['<h2>ERROR</h2>', '<errorMessage>', '<error>', '>ERROR<']
    for error in errors:
        if error in xml:
            return False
    if 'http://www.w3.org/' not in xml:
        return False
    return True


def canfly(wind_speed, rain_prob, temperature):
    '''Given the passed elements, returns a 2-element tuple.

    Arguments:
        wind_speed - float or integer wind speed in MPH units
        rain_prob - float or integer in range 1..100
        temperature - float or integer outside temp in Fahrenheit
    
    Returns a tuple consisting of:
    The first element is a short and concise string answer (ex. yes or no).
    The second element is an optional longer, sometimes witty, string about
    the current state of the weather.'''

    messages = {
        'freezing': ['It is really freakin\' cold!', 'This is parka weather.', 'It is below freezing!'],
        'nowind': ['Not much wind.', 'Hardly a whisper.'],
        'precip': ['Rain today!', 'It might be wet!'],
        'muchwind': ['Too much wind!', 'You\'ll get blown over!']
    }

    def pickmsg(key):
        '''Returns a random choice from the dict key provided.'''
        return rand.choice(messages[key])

    if wind_speed < 4:
        return ('No', pickmsg('nowind'))
    elif wind_speed > 30:
        return ('No', pickmsg('muchwind'))
    elif rain_prob > 40:
        return('No', pickmsg('precip'))
    elif float(temperature) <= 20:
        return('No', pickmsg('freezing'))
    else:
        return('Yes', 'Why not?')