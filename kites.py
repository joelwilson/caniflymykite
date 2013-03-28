import csv
from collections import defaultdict


class Kite(dict):
    '''Class containing kites information.'''
    def __init__(self, **kwargs):
        unicode_kwargs = kwargs
        for key, item in kwargs.iteritems():
            unicode_kwargs[key] = item.decode('utf-8')
        # call the dict objs init method, letting it do the dict setup magic
        super(Kite, self).__init__(**unicode_kwargs)
        # u'\u2727'


def get_kites(csvfile='./static/kites.csv'):
    '''Returns a dict of kites from a CSV file.'''
    kites = defaultdict(list)
    with open(csvfile, 'r') as kite_csv:
        kitereader = csv.DictReader(kite_csv)
        for row in kitereader:
            kites[row['category']].append(Kite(**row))
    return kites