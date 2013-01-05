from nose.tools import *

from noaa import *


class TestNOAA():
    def setUp(self):
        with open('./tests/ndfdXMLclient.xml') as f:
            self.test_xml = f.read()

            
    def tearDown(self):
        pass

        
    def test_between(self):
        assert_true(between(23.4, 20, 40))
        assert_true(between(1, 1, 10))
        assert_true(between(10, 1, 10))
        assert_true(between(230.928, 215, 500))
        assert_true(between(17.5, 10, 20))
        
        assert_false(between(1, 2, 4))
        assert_false(between(1.12, 1.2, 2))
        assert_false(between(100, 1, 99))
        assert_false(between(5.99999, 6, 10))
        assert_false(between(31, 5, 30))
        
        
    def test_headings(self):
        assert_equal(heading(0),   'N')
        assert_equal(heading(45),  'NE')
        assert_equal(heading(90),  'E')
        assert_equal(heading(135), 'SE')
        assert_equal(heading(180), 'S')
        assert_equal(heading(225), 'SW')
        assert_equal(heading(270), 'W')
        assert_equal(heading(315), 'NW')
        assert_equal(heading(360), 'N')
        assert_equal(heading(325.7), 'NW')
        assert_equal(heading(5), 'N')
        assert_equal(heading('5'), 'N')
        assert_equal(heading(359.3), 'N')
        assert_equal(heading('359.3'), 'N')
        assert_equal(heading(112.5), 'E')
        assert_equal(heading('112.5'), 'E')
        assert_equal(heading(110), 'E')
        assert_equal(heading('110'), 'E')
        
        
    def test_tomph(self):
        assert_equal(tomph(7), 8.06)
        assert_equal(tomph(14), 16.11)
        assert_equal(tomph(27), 31.07)
        assert_equal(tomph(3.81034), 4.38)
        assert_equal(tomph(1), 1.15)
        assert_equal(tomph(12.82, 4), 14.753)
        assert_equal(tomph(1, 4), 1.1508)
        
        
    @raises(TypeError, ValueError)
    def test_mph_error(self):
        tomph('blah')
        tomph('15')
        
        
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
