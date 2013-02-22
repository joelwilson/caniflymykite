import json

from nose.tools import *

import geonames as gn


class TestGeonames():
    def setUp(self):
        with open('./config/config.json') as _file:
            self.user = json.loads(_file.read())['geonames_user']

    def tearDown(self):
        pass

    def test_search_results(self):
        assert_greater(len(gn.search('turlock')['geonames']), 0)
        assert_greater(len(gn.search('los banos, ca')['geonames']), 0)
        assert_greater(len(gn.search('San Francisco, CA')['geonames']), 0)
        assert_greater(len(gn.search('kansas city')['geonames']), 0)
        assert_greater(len(gn.search('miami')['geonames']), 0)

    def test_search_no_results(self):
        assert_list_equal(gn.search('blahblah123')['geonames'], [])
        assert_list_equal(gn.search('Ghubaysh')['geonames'], [])
        assert_list_equal(gn.search('Dushanbe')['geonames'], [])
        assert_list_equal(gn.search('Yeruham')['geonames'], [])