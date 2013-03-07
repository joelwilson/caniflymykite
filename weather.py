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
        self.elements = {
            'lat': float(lat),
            'lon': float(lon),
            'wind_speed': tomph(self.forecast.get('wind_speed')),
            'wind_dir': heading(self.forecast.get('wind_dir')),
            'rain_prob': self.forecast.get('rain_prob'),
            'temperature': self.forecast.get('temperature')
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
                raise WeatherError(e)
            self.elements['datetime'] = self.current['datetime']
            self.elements['stationlat'] = self.current['lat']
            self.elements['stationlon'] = self.current['lng']
            self.elements['stationname'] = self.current['stationName']
            self.elements['stationid'] = self.current['ICAO']

    def __getitem__(self, key):
        return self.elements[key]


def forecast(lat, lon):
    '''Helper function for retrieving forecast data from the NOAA.'''
    return noaa.forecast(lat, lon)

def currentweather(lat, lon):
    '''Helper function for retrieving current weather data from a
    weather station nearest to the given lat, lon point.'''
    return gn.weather(lat, lon)