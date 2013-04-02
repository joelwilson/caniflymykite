import noaa
import geonames as gn
from utils import heading, tomph, ctof


class WeatherError(Exception):
    '''Basic exception class for exceptions in the Forecast class.'''
    pass


class Weather(object):
    '''Object containing weather information for a lat, lon point.'''
    def __init__(self, lat, lon):
        self.forecast = forecast(lat, lon)
        self.current = currentweather(lat, lon)
        self.place = gn.nearestplace(lat, lon)
        self.elements = {
            'lat': float(lat),
            'lon': float(lon),
            'wind_speed': tomph(self.forecast.get('wind_speed')),
            'wind_dir': heading(self.forecast.get('wind_dir')),
            'rain_prob': self.forecast.get('rain_prob'),
            'temperature': self.forecast.get('temperature'),
            'city_name': self.place['name'],
            'state': self.place['adminCode1']
        }
        if self.current is not None:
            self.elements['wind_speed'] = tomph(
                                          self.current['windSpeed'])
            self.elements['temperature'] = ctof(
                                           self.current['temperature'])
            try:
                self.elements['wind_dir'] = heading(
                                            self.current['windDirection'])
            except KeyError:
                pass
            self.elements['datetime'] = self.current['datetime']
            self.elements['stationlat'] = self.current['lat']
            self.elements['stationlon'] = self.current['lng']
            self.elements['stationname'] = self.current['stationName']
            self.elements['stationid'] = self.current['ICAO']
        self.elements['canfly'] = noaa.canfly(
            self.elements['wind_speed'],
            self.elements['rain_prob'],
            self.elements['temperature']
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
    place = gn.search(location)[0]
    return Weather(place['lat'], place['lng'])

def getbylatlon(lat, lon):
    '''Returns a Weather object for the given lat, lon.'''
    return Weather(lat, lon)