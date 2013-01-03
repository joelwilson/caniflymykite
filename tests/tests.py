from nose.tools import *
import requests

from noaa import *
import app


class TestNOAA():
    def setUp(self):
        with open('./tests/ndfdXMLclient.xml') as f:
            self.test_xml = f.read()

    def tearDown(self):
        pass

    def test_mph(self):
        assert_equal(mph(7), 8.06)
        assert_equal(mph(14), 16.11)
        assert_equal(mph(27), 31.07)
        assert_equal(mph(3.81034), 4.38)
        assert_equal(mph(1), 1.15)
        assert_equal(mph(12.82, 4), 14.753)
        assert_equal(mph(1, 4), 1.1508)
        
        
    @raises(TypeError)
    def test_mph_error(self):
        mph('blah')
        mph('15')
        
        
    def test_isvalid_xml_strings(self):
        assert_true(isvalid(self.test_xml))
        assert_false(isvalid('<xml><weather></weather></xml>'))
        assert_false(isvalid('Izzy is a cat'))


    def test_isvalid_query_noaa(self):
        assert_true(isvalid(query_noaa(90210, ['sky'])))
        assert_true(isvalid(query_noaa(95382, ['sky', 'snow'])))
        assert_true(isvalid(query_noaa(12345, ['wdir', 'wguest'])))
        assert_true(isvalid(query_noaa(93635, ['wdir', 'wguest', 'blah'])))
        
        assert_false(isvalid(query_noaa(9021, ['wsp', 'temp'])))
        assert_false(isvalid(query_noaa(42, ['wsp', 'temp'])))
        assert_false(isvalid(query_noaa('Santa Monica', ['sky', 'pop12'])))


    def test_parse_xml(self):
        assert_is_instance(parse_xml(self.test_xml), dict)
        assert len(parse_xml(query_noaa(90210, NOAA_ELEMS))) > 1


    def test_get_weather(self):
        assert_raises(WeatherError, get_weather, 1985, NOAA_ELEMS)
        assert_is_instance(get_weather(11005, NOAA_ELEMS), Weather)
        
        w = get_weather(95382, ['sky', 'wdir', 'wsp'])
        assert_equals(w.latlon, ('37.54', '-120.85'))
        assert_is_instance(w.times, dict)
        assert_is_instance(w.weather, dict)
    
    
class TestApp():
    pass