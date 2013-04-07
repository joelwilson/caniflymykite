import json
import os

import requests


USERNAME = os.environ['GEONAMES_USER']
BASE_URL = 'http://api.geonames.org'


def search(term, user=USERNAME):
    '''Returns a dict of results for a search to geonames.'''
    r = requests.get(BASE_URL + '/searchJSON', 
                     params={'q': term,
                             'username': user,
                             'country': 'US',
                             'featureClass': 'P'})
    return json.loads(r.text)['geonames'] if r.ok else None


def weather(lat, lon, user=USERNAME):
    '''Returns a dict of current weather conditions of the station
    closest to lat, lon.
    '''
    r = requests.get(BASE_URL + '/findNearByWeatherJSON',
                     params={'lat': lat,
                             'lng': lon,
                             'username': user})
    jsontext = json.loads(r.text)
    if r.ok:
        try:
            return jsontext['weatherObservation']
        except KeyError:
            return None
    return None


def nearestplace(lat, lon, user=USERNAME):
    ''''Returns a dict of attributes of the closest geographical place.'''
    r = requests.get(BASE_URL + '/findNearbyPlaceNameJSON',
                     params={'lat': lat,
                             'lng': lon,
                             'username': user,
                             'country': 'US',
                             'featureClass': 'P'})
    jsontext = json.loads(r.text)
    if r.ok:
        try:
            return jsontext['geonames'][0]
        except KeyError:
            return None
    return None