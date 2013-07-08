from datetime import datetime

import noaa
import geonames as gn
import wunderground
from utils import heading, tomph, ctof, iszip


def weather_memo(f):
    '''Memoization decorator for caching the results of initiating
    Weather objects.'''
    cache = {}
    def memoized(x, sec):
        if x not in cache or (x in cache and cache[x].age() <= sec):
            cache[x] = f(x)
        return cache[x]
    return memoized


class WeatherError(Exception):
    '''Basic exception class for exceptions in the Forecast class.'''
    pass


class Weather(object):
    '''Object containing weather information for a lat, lon point.'''
    def __init__(self, query):
        '''Given a query/search text, populates the weather info.'''
        self.raw = wunderground.conditions_and_forecast(query)    
        tries = 3
        # Wunderground does something wierd if it has more than 1 match
        # for a location. It returns an intermediate-like json response
        # containing each location it has that are close matches. We will
        # try the first match automatically until a  true match is found.
        # Otherwise, give up after 'tries' are depleted.
        while tries > 0:
            with open('tries.txt', 'a') as _file:
                _file.write(str(self.raw))
            tries -= 1
            # Let's assume we have a match
            try:
                self.forecast = self.raw['forecast']['simpleforecast']['forecastday']
                self.current = self.raw['current_observation']
                self.load_elements()
                break
            # No match, let's try again
            except KeyError, e:
                if 'error' in self.raw['response'].keys():
                    raise WeatherError(self.raw['response']['error']['type'])
                self.raw = wunderground.conditions_and_forecast(
                    '{city}, {state} {country}'.format(
                        city=self.raw['response']['results'][0]['city'],
                        state=self.raw['response']['results'][0]['state'],
                        country=self.raw['response']['results'][0]['country_name']
                    )
                )

    def load_elements(self):
        self.elements = {
            # Date & Time
            'creation_time': datetime.utcnow(),
            'time_text': self.current['observation_time'],
            'time_epoch': float(self.current['local_epoch']),
            'time_offset': int(self.current['local_tz_offset']),
            'time_local': datetime.fromtimestamp(float(self.current['local_epoch'])),
            'time_utc': datetime.utcfromtimestamp(float(self.current['local_epoch'])),
            # Location info  
            'full_name': self.current['display_location']['full'],
            'city': self.current['display_location']['city'],
            'state': self.current['display_location']['state'],
            'country': self.current['display_location']['country'],
            'lat': self.current['display_location']['latitude'],
            'lon': self.current['display_location']['longitude'],
            # Station info
            'station_id': self.current['station_id'],
            'station_name': self.current['observation_location']['full'],
            'station_lat': self.current['observation_location']['latitude'],
            'station_lon': self.current['observation_location']['longitude'],
            # Current conditions info
            'wind_mph': self.current['wind_mph'],
            'wind_kph': self.current['wind_kph'],
            'wind_dir': heading(self.current['wind_degrees']),
            'wind_gust_kph': self.current['wind_gust_kph'],
            'wind_gust_mph': self.current['wind_gust_mph'],
            'temp_f': int(self.current['temp_f']),
            'temp_c': int(self.current['temp_c']),
            'weather': self.current['weather'],
            # Forecast info
            'rain_prob': self.forecast[0]['pop']
        }
        self.elements['canfly'] = noaa.canfly(
            self.elements['wind_mph'],
            self.elements['rain_prob'],
            self.elements['temp_f']
        )

    def observation_age(self):
        '''Return the number of seconds since the weather observation.'''
        return (datetime.utcnow() - self.elements['time_utc']).seconds

    def age(self):
        '''Returns the number of seconds since object creation.'''
        return (datetime.utcnow() - self.elements['creation_time']).seconds

    def __getitem__(self, key):
        return self.elements[key]

    def __setitem__(self, key, value):
        self.elements[key] = value
 
    def __delitem__(self, key):
        del self.elements[key]

    def __len__(self):
        return len(elements)

    def __str__(self):
        return str(self.elements)


def forecast(lat, lon):
    '''Helper function for retrieving forecast data from the NOAA.'''
    return noaa.forecast(lat, lon)


def currentweather(lat, lon):
    '''Helper function for retrieving current weather data from a
    weather station nearest to the given lat, lon point.'''
    return gn.weather(lat, lon)


@weather_memo
def getbyquery(query, sec=300):
    return Weather(query)


def getbylocation(location):
    '''Returns a Weather object for the given location name.'''
    if iszip(location):
        lat, lon = noaa.ziplatlon(int(location))
        return Weather(lat, lon)
    else:
        place = gn.search(location)[0]
        return Weather(place['lat'], place['lng'])


def getbylatlon(lat, lon):
    '''Returns a Weather object for the given lat, lon.'''
    return Weather(lat, lon)
