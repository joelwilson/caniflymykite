from nose.tools import *

from weather import Weather


class TestWeather():
    def test_weather_turlock():
        weather = Weather(37.52, -120.849)
        assert_equal()