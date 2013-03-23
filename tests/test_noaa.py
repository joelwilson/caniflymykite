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
        assert_true(isvalid(query_noaa(34.076, -118.3953, ['sky', 'temp'])))
        assert_true(isvalid(query_noaa(37.5239, -120.8520, ['sky', 'snow', 'temp'])))
        assert_true(isvalid(query_noaa(42.8142, -73.9395, ['wdir', 'wguest'])))
        assert_true(isvalid(query_noaa(37.0626, -120.8543, ['wdir', 'wguest', 'blah'])))

        assert_false(isvalid(query_noaa(1324, 2213, ['wsp', 'temp'])))
        assert_false(isvalid(query_noaa('Turlock', 'CA', ['wsp', 'temp'])))
        assert_false(isvalid(query_noaa(1232, -5009, ['sky', 'pop12'])))

    def test_parse_xml(self):
        assert_is_instance(parse_forecast_xml(self.test_xml), dict)
        assert len(parse_forecast_xml(query_noaa(34.076, -118.3953, NOAA_ELEMS))) > 1

    def test_get_forecast(self):
        assert_raises(ForecastError, forecast, 1985, NOAA_ELEMS)
        assert_is_instance(forecast(40.756, -73.715, NOAA_ELEMS), Forecast)
        
        w = forecast(37.5239, -120.8520, ['sky', 'wdir', 'wsp'])
        assert_equals(w.latlon, (37.52, -120.85))
        assert_is_instance(w.times, dict)
        assert_is_instance(w.weather, dict)

    def test_can_fly(self):
        assert_equals(canfly(12, 0, 80)[0].upper(), 'YES')
        assert_equals(canfly(12, 30, 65)[0].upper(), 'YES')
        assert_equals(canfly(3, 0, 76)[0].upper(), 'NO')
        assert_equals(canfly(8.2, 15.6, 30)[0].upper(), 'YES')
        assert_equals(canfly(12.02, 50.55, 65)[0].upper(), 'NO')