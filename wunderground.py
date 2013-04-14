import json
import os

import requests


API_KEY = os.environ['WUNDERGROUND_KEY']


def query_wunderground(api_key, features, query, file_format="json"):
    '''Generic API query function for making any query to the Wunderground
    API and returning the JSON result. Probably re-inventing the wheel, 
    but oh well.'''
    baseurl = 'http://api.wunderground.com/api/'
    r = requests.get(
        baseurl + '{key}/{features}/q/{query}.{format}'.format(
            key=api_key,
            features='/'.join(features),
            query=str(query).strip(),
            format=file_format
        )
    )
    return json.loads(r.text)


def conditions_and_forecast(query):
    '''Returns a dict containing forecast and current conditions for
    the location in query.'''
    return query_wunderground(API_KEY, ['conditions', 'forecast'], query)
    

def current_conditions(query):
    '''Searches Wunderground for a location matching the given query. 
    Returns a dict of results as returned from Wunderground.'''
    return query_wunderground(API_KEY, ['conditions'], query)


def forecast(query):
    '''Searches Wunderground for a location matching the given query and
    returns the 3 day forecast for the location.'''
    return query_wunderground(API_KEY, ['forecast'], query)

if __name__ == '__main__':
    from pprint import pprint
    pprint(conditions_and_forecast(97217))
