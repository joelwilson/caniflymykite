from nose.tools import *

import cifmk


class TestWebApp():
    def setUp(self):
        cifmk.app.config['TESTING'] = True
        self.app = cifmk.app.test_client()
        
    def tearDown(self):
        pass
        
    def test_bogus_urls(self):
        assert_equals(self.app.get('1212121212121212').status_code, 404)
        assert_equals(self.app.get('bogus').status_code, 404)
        assert_equals(self.app.get('/<alert>"Oh hai"</alert>').status_code, 404)
        assert_equals(self.app.get('!*$@)//#@').status_code, 404)
        assert_equals(self.app.get('there was an old lady').status_code, 404)
    
    def test_valid_zip_urls(self):
        assert_equals(
            self.app.get('/weather?location=' + '10005').status_code, 200)
        assert_equals(
            self.app.get('/weather?location=' + '20555').status_code, 200)
        assert_equals(
            self.app.get('/weather?location=' + '90210').status_code, 200)
        assert_equals(
            self.app.get('/weather?location=' + '22202').status_code, 200)
        assert_equals(
            self.app.get('/weather?location=' + '06390').status_code, 200)
        assert_equals(
            self.app.get('/weather?location=' + '41075').status_code, 200)
        assert_equals(
            self.app.get('/weather?location=' + '07188').status_code, 200)
        assert_equals(
            self.app.get('/weather?location=' + '12214').status_code, 200)
        assert_equals(
            self.app.get('/weather?location=' + '95382').status_code, 200)            

    def test_valid_location_string_urls(self):
        locations = ['Turlock', 'Modesto, CA', 'Seattle, wa', 'Santa monica',
                     'New York, NY', 'Miami', 'Las Vegas', 'Butte', 'Chico']
        for u in locations:
            rv = self.app.get('/weather?location=' + u)
            assert_equals(rv.status_code, 200, msg=u + ' ' + rv.status)