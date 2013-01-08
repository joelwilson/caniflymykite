from nose.tools import *

import cifmk


class TestWebApp():
    def setUp(self):
        cifmk.app.config['TESTING'] = True
        self.app = cifmk.app.test_client()
        
    def tearDown(self):
        pass
        
    def test_bogus_urls(self):
        urls = ['1212121212121212', 'bogus', '/<alert>"Oh hai"</alert>',
                'google.com', '!*$@)//#@', 'there was an old lady']
        for u in urls:
            rv = self.app.get(u)
            assert_equals(rv.status, '404 NOT FOUND')
            
    def test_non_existant_zips(self):
        pass
    
    def test_valid_urls(self):
        urls = ['10005', '20555', '90210', '22202', '06390', '42223',
                '07188', '12214']
        for u in urls:
            rv = self.app.get('/zip/' + u)
            assert_equals(rv.status, '200 OK', msg=u)
            assert_in(u, rv.data, msg=u)