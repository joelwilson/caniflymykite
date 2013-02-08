from nose.tools import *

from noaa import *
from noaa import _distance, _closest_point, _between


class TestNOAA():
    def setUp(self):
        with open('./tests/ndfdXMLclient.xml') as f:
            self.test_xml = f.read()

    def tearDown(self):
        pass

    def test_between(self):
        assert_true(_between(23.4, 20, 40))
        assert_true(_between(1, 1, 10))
        assert_true(_between(10, 1, 10))
        assert_true(_between(230.928, 215, 500))
        assert_true(_between(17.5, 10, 20))

        assert_false(_between(1, 2, 4))
        assert_false(_between(1.12, 1.2, 2))
        assert_false(_between(100, 1, 99))
        assert_false(_between(5.99999, 6, 10))
        assert_false(_between(31, 5, 30))

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
        
    def test_iszip(self):
        assert_true(iszip, 90120)
        assert_true(iszip, 12345)
        assert_true(iszip, '90120')
        
        assert iszip('90120111') is False
        assert iszip('what!') is False
        assert iszip(102010201020) is False

    def test_closest_point(self):
        assert_equals(_closest_point((12, 10.5), [(12, 12), (-12, -10.5)]), (12, 12))
        assert_equals(_closest_point((-34.32, 89), [(-40, 100), (-33, -100)]), (-40, 100))
        assert_equals(_closest_point((1, 0), [(0, 0), (0, 1)]), (0, 0))
        assert_equals(_closest_point((134.999, 67.234), [(120, -70), (130, 55)]), (130, 55))
        assert_equals(_closest_point((23, -90), [(19.342, 0), (23, 180)]), (23, 180))

    def test_distance(self):
        assert_equals(_distance((60, 120), (80, 50)), 3119)
        assert_equals(_distance((16.75, -62.167), (27.182, -80.221)), 2189)
        assert_equals(_distance((26.612, -80.862), (27.182, -80.221)), 89.76)
        assert_equals(_distance((34.983, -117.867), (43.4, -70.7)), 4114)
        assert_equals(_distance((39.14, -121.44), (35.43, -119.05)), 463.5)
        assert_equals(_distance((34.09, -118.03), (34.02, -118.28)), 24.31)

    def test_can_fly(self):
        assert_equals(canfly(12, 0, 80)[0].upper(), 'YES')
        assert_equals(canfly(12, 30, 65)[0].upper(), 'NO')
        assert_equals(canfly(4, 0, 76)[0].upper(), 'NO')

    def test_current_conditions(self):
        assert_is_not_none(current_conditions('KP60'))
        assert_is_not_none(current_conditions('TAPA'))
        assert_is_not_none(current_conditions('TPLM2'))
        assert_is_not_none(current_conditions('KBHB'))        
        assert_is_not_none(current_conditions('KP60')['wind_speed'])
        assert_is_not_none(current_conditions('TAPA')['wind_speed'])
        assert_is_not_none(current_conditions('TPLM2')['wind_speed'])
        assert_is_not_none(current_conditions('KBHB')['wind_speed'])
        
    def test_current_conditions(self):
        pass