import csv
from collections import defaultdict


class Kite(dict):
    '''Class containing kites information.'''
    def __init__(self, *arg, **kwargs):
        super(Kite, self).__init__(*arg, **kwargs)
        #self['difficulty'] = (u'\u2726' * int(self['difficulty']))
        self._make_ratings()
        
    def _make_ratings(self):
        '''Converts the numerical ratings into visual strings.'''
        try:
            self['difficulty'] = self._rating_string('difficulty')
            self['power'] = self._rating_string('power')
            self['speed'] = self._rating_string('speed')
            self['price'] = self._rating_string('price')
        except ValueError:
            pass

    def _rating_string(self, key, tick=u'\u2726', notick=u'\u2727'):
        '''Returns a string containing 5 characters representing the
        rating.'''
        num_ticks = int(self[key])
        return (tick * num_ticks + notick * (5 - num_ticks))


def get_kites(csvfile='./static/kites.csv'):
    '''Returns a dict of kites from a CSV file.'''
    kites = defaultdict(list)
    with open(csvfile, 'r') as kite_csv:
        kitereader = csv.DictReader(kite_csv)
        for row in kitereader:
            kites[row['category']].append(Kite(row))
    return kites