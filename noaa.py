import xml.etree.cElementTree as ET
import random as rand
import math
from datetime import datetime
from collections import defaultdict

import requests


__all__ = ['Weather', 'get_weather', 'query_noaa', 'WeatherError', 
           'current_conditions', 'parse_forecast_xml', 'isvalid', 
           'tomph', 'NOAA_ELEMS', 'heading', 'iszip', 'canfly',
           'StationList']
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


class WeatherError(Exception):
    '''Basic exception class for exceptions in the Weather class.'''
    pass


class Weather(object):
    '''Container class for storing and retrieving weather data.
    Input is the XML response text retrieved from an NOAA query. Weather
    elements are accessed by name using the val() function.
    '''
    def __init__(self, xml):
        if not isvalid(xml):
            raise WeatherError('Invalid XML data: \n{0}'.format(xml))
        else:
            parsed = parse_forecast_xml(xml)
        self.latlon = (parsed['latitude'], parsed['longitude'])
        self.times = parsed['times']
        self.weather = parsed['weather']

    def val(self, element, when=datetime.now(), debug=False):
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


class StationList(object):
    '''Class for storing, refreshing, and retrieving a list of weather
    stations provided by weather.gov.'''
    def __init__(self, station_list=None,
                 url='http://w1.weather.gov/xml/current_obs/index.xml'):
        self.url = url
        if station_list is None:
            self.refresh()
        else:
            self.stations = station_list

    def refresh(self):
        '''Fetches and parses the current station list from weather.gov.'''
        self.stations = self._parse_station_list(requests.get(self.url).text)

    def conditions(self, location):
        '''Given a station ID string or lat, lon tuple, returns the current
        weather conditions.'''
        if isinstance(location, tuple):
            closest = min(self.stations, 
                          key=lambda p: _distance(location, p[2]))
            return closest, current_conditions(closest[0])
        elif isinstance(location, basestring):
            return current_conditions(location)

    def _parse_station_list(self, xmltxt):
        '''Given the xml text from the weather.gov station list, returns
        a list of tuples containing the information for each station.'''
        root = ET.fromstring(xmltxt.encode('utf_8'))
        list_ = []
        for station in root.iter('station'):
            list_.append(
                (station.findtext('station_id'),
                 station.findtext('station_name'),
                 (float(station.findtext('latitude')),
                  float(station.findtext('longitude'))),
                 station.findtext('xml_url')))
        return list_

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.stations[0:5])

    def __str__(self):
        return self.stations


def current_conditions(stationid):
    '''Returns a dict of current weather conditions for a given 
    stationid.'''
    r = requests.get('http://weather.gov/xml/current_obs/{0}.xml'.format(
                     stationid))
    if r.status_code != 200:
        return None
    else:
        root = ET.fromstring(r.text)
        return {'location': root.findtext('location'),
                'temperature': root.findtext('temp_f'),
                'humidity': root.findtext('relative_humidity'),
                'wind_dir': root.findtext('wind_degrees'),
                'wind_speed': root.findtext('wind_kt')}


def get_weather(zipcode, elems=NOAA_ELEMS):
    '''Returns weather data for a zip code as an instance of a weather
    data class.'''
    xml = query_noaa(zipcode, elems)
    return Weather(xml)


def query_noaa(zipcode, elems, url=URL):
    '''Returns the XML text returned by a query to NOAA with the passed
    zipcode and list or tuple of weather elements, elems.'''
    params = {
        'zipCodeList': zipcode,
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
    errors = ['<h2>ERROR</h2>', '<errorMessage>', '<error>']
    for error in errors:
        if error in xml:
            return False
    if 'http://www.w3.org/' not in xml:
        return False
    return True


def iszip(zipcode):
    '''Returns True is the provided zip code is valid.'''
    xml = query_noaa(zipcode, ['sky'])
    if isvalid(xml):
        return True
    else:
        return False


def tomph(knots, precision=2):
    '''Converts knots to MPH.'''
    return round(float(knots) * 1.15078, precision)


def heading(deg):
    '''Returns a string representation of an numerical direction in degrees.

    Examples:
        heading(360) => "N"
        heading('45')  => "NE"
    '''
    deg = float(deg)
    head = {
        'N1':  (0,     22.5),
        'NE':  (22.6,  67.5),
        'E':   (67.6,  112.5),
        'SE':  (112.6, 157.5),
        'S':   (157.6, 202.5),
        'SW':  (202.6, 247.5),
        'W':   (247.6, 292.5),
        'NW':  (292.6, 337.5),
        'N2':  (337.6, 360.0)
    }
    for key, val in head.iteritems():
        if _between(deg, *val):
            return 'N' if key == 'N1' or key == 'N2' else key
    return None


def canfly(weather):
    '''Given the passed weather object, returns a 2-element tuple.

    The first element is a short and concise string answer (ex. yes or no).
    The second element is an optional longer, sometimes witty, string about
    the current state of the weather.'''

    messages = {
        'freezing': ['This is parka weather.', 'It is freezing!'],
        'nowind': ['Not much wind.', 'Hardly a whisper.'],
        'precip': ['Rain today!', 'It might be wet!']
    }

    def pickmsg(key):
        '''Returns a random choice from the dict key provided.'''
        return rand.choice(messages[key])

    if tomph(weather.val('wind_speed')) < 5:
        return ('No', pickmsg('nowind'))
    else:
        if int(weather.val('rain_prob')) > int(20):
            return('No', pickmsg('precip'))
        else:
            if weather.val('temperature') <= 32:
                return('No', pickmsg('freezing'))
            else:
                return('Yes', 'Why not?')


def _between(num, low, high):
    '''Returns True if num between low & high (inclusive), else False.'''
    return True if num >= low and num <= high else False


def _closest_point(start, points):
    '''Returns the point of the form (lat, lon) in a list of points which
    is closest to the starting point.'''
    return min(points, key=lambda p: _distance(start, p))


def _distance(start, end):
    '''Returns the distance (kilometers) between two points on the Earth.
    
    Uses the Spherical Law of Cosines to calculate distance.'''
    R = 6371        # Earth's radius
    start = (math.radians(start[0]), math.radians(start[1]))
    end = (math.radians(end[0]), math.radians(end[1]))
    d = (math.acos(math.sin(start[0]) * math.sin(end[0]) +
         math.cos(start[0]) * math.cos(end[0]) *
         math.cos(end[1] - start[1])) * R)
    return (round(d, 2) if len(str(d).split('.')[0]) <= 2 else
            round(d, 1) if len(str(d).split('.')[0]) == 3 else
            round(d))