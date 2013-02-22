import json

import requests


with open('./config/config.json') as _file:
    USERNAME = json.loads(_file.read())['geonames_user']
BASE_URL = 'http://api.geonames.org'


def search(term, num_results=25, user=USERNAME):
    '''Returns a dict of results for a search to geonames.
    
    Docs: http://www.geonames.org/export/geonames-search.html
    '''
    r = requests.get(BASE_URL + '/searchJSON', 
                     params={'q': term,
                             'username': user,
                             'country': 'US',
                             'featureClass': 'P'})
    return json.loads(r.text) if r.ok else None


def weather(lat, lon, user=USERNAME):
    '''Returns a dict current weather conditions of the station
    closest to lat, lon.
    
    Docs: http://www.geonames.org/export/JSON-webservices.html#findNearByWeatherJSON'''
    r = requests.get(BASE_URL + '/findNearByWeatherJSON',
                     params={'lat': lat,
                             'lng': lon,
                             'username': user})
    return json.loads(r.text) if r.ok else None