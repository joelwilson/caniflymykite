from nose.tools import *

from utils import tomph, between, heading, closest_point, distance, ctof, iszip, rem_chars


class TestUtils():
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

    @raises(TypeError, ValueError)
    def test_mph_error(self):
        tomph('blah')
        tomph('15')

    def test_tomph(self):
        assert_equal(tomph(7), 8.1)
        assert_equal(tomph(14), 16.1)
        assert_equal(tomph(27), 31.1)
        assert_equal(tomph(3.81034), 4.4)
        assert_equal(tomph(1), 1.2)
        assert_equal(tomph(12.82, 3), 14.753)
        assert_equal(tomph(1, 4), 1.1508)

    def test_heading(self):
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

    def test_closest_point(self):
        assert_equals(closest_point((12, 10.5), [(12, 12), (-12, -10.5)]), (12, 12))
        assert_equals(closest_point((-34.32, 89), [(-40, 100), (-33, -100)]), (-40, 100))
        assert_equals(closest_point((1, 0), [(0, 0), (0, 1)]), (0, 0))
        assert_equals(closest_point((134.999, 67.234), [(120, -70), (130, 55)]), (130, 55))
        assert_equals(closest_point((23, -90), [(19.342, 0), (23, 180)]), (23, 180))

    def test_distance(self):
        assert_equals(distance((60, 120), (80, 50)), 3119)
        assert_equals(distance((16.75, -62.167), (27.182, -80.221)), 2189)
        assert_equals(distance((26.612, -80.862), (27.182, -80.221)), 89.76)
        assert_equals(distance((34.983, -117.867), (43.4, -70.7)), 4114)
        assert_equals(distance((39.14, -121.44), (35.43, -119.05)), 463.5)
        assert_equals(distance((34.09, -118.03), (34.02, -118.28)), 24.31)

    def test_ctof(self):
        assert_equals(ctof(0), 32.0)
    
    def test_iszip(self):
        assert_true(iszip('90210'))
        assert_true(iszip(12345))
        assert_false(iszip(''))
        assert_false(iszip('654321'))