from nose.tools import *

from weather import Weather


class TestWeather():
    def test_weather_modesto(self):
        weather = Weather(37.6392, -120.9958)
        assert_is_not_none(weather.current)
        assert_equals(weather['stationid'], u'KMOD')
        assert_is_not_none(weather['wind_speed'])
        assert_is_not_none(weather['temperature'])
        assert_is_not_none(weather['wind_speed'])  