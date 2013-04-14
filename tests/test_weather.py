from nose.tools import *

from weather import Weather


class TestWeather():
    def test_weather_modesto(self):
        weather = Weather('Modesto, ca')
        assert_is_not_none(weather.current)
        assert_in('station_id', weather.elements.keys())
        assert_is_not_none(weather['wind_mph'])
        assert_is_not_none(weather['temp_f'])
        assert_is_not_none(weather['canfly'])
        
    def test_weather_san_francisco(self):
        weather = Weather('San Francisco, ca')
        assert_is_not_none(weather.current)
        assert_in('station_id', weather.elements.keys())
        assert_is_not_none(weather['wind_mph'])
        assert_is_not_none(weather['temp_f'])
        assert_is_not_none(weather['canfly'])  
