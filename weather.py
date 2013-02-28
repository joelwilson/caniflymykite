import noaa
import geonames as gn
from utils import heading, tomph, ctof


class WeatherError(Exception):
    '''Basic exception class for exceptions in the Forecast class.'''
    pass


class Weather(object):
    def __init__(self, lat, lon):
        self.forecast = noaa.forecast(lat, lon)
        self.current = gn.weather(lat, lon)
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
            
    def __getitem__(self, key):
        return self.elements[key]