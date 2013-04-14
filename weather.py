import noaa
import geonames as gn
import wunderground
from utils import heading, tomph, ctof, iszip


class WeatherError(Exception):
    '''Basic exception class for exceptions in the Forecast class.'''
    pass


class Weather(object):
    '''Object containing weather information for a lat, lon point.'''
    def __init__(self, query):
        '''Given a query/search text, populates the weather info.'''
        self.raw = wunderground.conditions_and_forecast(query)       
        found = False
        tries = 3
        # Wunderground does something wierd if it has more than 1 match
        # for a location. It returns an intermediate-like json response
        # containing each location it has that are close matches. We will
        # try the first match automatically until a match is found.
        # Otherwise, give up after 'tries' are up.
        while not found:
            tries -= 1
            # Let's assume it gave a match
            try:
                self.forecast = self.raw['forecast']['simpleforecast']['forecastday']
                self.current = self.raw['current_observation']
                found = True
            # No match, let's try again
            except KeyError, e:
                self.raw = wunderground.conditions_and_forecast(
                    '{city}, {state} {country}'.format(
                        city=self.raw['response']['results'][0]['city'],
                        state=self.raw['response']['results'][0]['state'],
                        country=self.raw['response']['results'][0]['country_name']
                    )
                )
            # did we find it?
            if tries == 0 and not found:
                break
        self.elements = {
            # Location info  
            'city_name': self.current['display_location']['city'],
            'state': self.current['display_location']['state'],
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
