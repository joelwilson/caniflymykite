import json
import os

from nose.tools import *

import geonames as gn


class TestGeonames():
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_search_yes_results(self):
        assert_greater(len(gn.search('turlock')), 0)
        assert_greater(len(gn.search('los banos, ca')), 0)
        assert_greater(len(gn.search('San Francisco, CA')), 0)
        assert_greater(len(gn.search('kansas city')), 0)
        assert_greater(len(gn.search('miami')), 0)
        assert_greater(len(gn.search('90210')), 0)

    def test_search_no_results(self):
        assert_list_equal(gn.search('blahblah123'), [])
        assert_list_equal(gn.search('Ghubaysh'), [])
        assert_list_equal(gn.search('Dushanbe'), [])
        assert_list_equal(gn.search('Yeruham'), [])

    def test_weather(self):
        assert_equal(gn.weather(37.5, -120)['ICAO'], 'KMAE')
        assert_equal(gn.weather(34, -118.4)['ICAO'], 'KSMO')
        