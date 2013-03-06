from nose.tools import *

from noaa import *


class TestNOAA():
    def setUp(self):
        with open('./tests/ndfdXMLclient.xml') as f:
            self.test_xml = f.read()

    def tearDown(self):
        pass

    def test_isvalid_xml_strings(self):
        assert_true(isvalid(self.test_xml))
        assert_false(isvalid('<xml><weather></weather></xml>'))
        assert_false(isvalid('Izzy is a cat'))

    def test_isvalid_query_noaa(self):
        assert_true(isvalid(query_noaa(34.076, -118.3953, ['sky'])))
        assert_true(isvalid(query_noaa(37.5239, -120.8520 ['sky', 'snow'])))
        assert_true(isvalid(query_noaa(42.8142, -73.9395 ['wdir', 'wguest'])))
        assert_true(isvalid(query_noaa(37.0626, -120.8543, ['wdir', 'wguest', 'blah'])))

        assert_false(isvalid(query_noaa(9021, ['wsp', 'temp'])))
        assert_false(isvalid(query_noaa(42, ['wsp', 'temp'])))
        assert_false(isvalid(query_noaa('Santa Monica', ['sky', 'pop12'])))

    def test_parse_xml(self):
        assert_is_instance(parse_forecast_xml(self.test_xml), dict)
        assert len(parse_forecast_xml(query_noaa(34.076, -118.3953, NOAA_ELEMS))) > 1

    def test_get_weather(self):
        assert_raises(WeatherError, get_weather, 1985, NOAA_ELEMS)
        assert_is_instance(get_weather(11005, NOAA_ELEMS), Weather)
        
        w = get_weather(95382, ['sky', 'wdir', 'wsp'])
        assert_equals(w.latlon, (37.54, -120.85))
        assert_is_instance(w.times, dict)
        assert_is_instance(w.weather, dict)

    def test_can_fly(self):
        assert_equals(canfly(12, 0, 80)[0].upper(), 'YES')
        assert_equals(canfly(12, 30, 65)[0].upper(), 'NO')
        assert_equals(canfly(4, 0, 76)[0].upper(), 'NO')