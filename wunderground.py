import json



def query_wunderground(api_key, features, query=False, file_format="JSON"):
    '''Generic API query function for making any query to the Wunderground
    API and returning the JSON result. Probably re-inventing the wheel, 
    but oh, well.'''
    baseurl = 'http://api.wunderground.com/api/'
    r = requests.get(baseurl + '{key}/{features}/q/{query}.{format}'.format(
                     {'key': api_key, 'features': '/'.join(features), 
                         'query': query.strip(), 'format': file_format}
    return json.loads(r.text)


def current_conditions_search(query):
    '''Searches Wunderground for a location matching the given query. 
    Returns a dict of results as returned from Wunderground.'''
    return query_wunderground(API_KEY, ['conditions'], query=query)


def three_day_forecast(query):
    '''Searches Wunderground for a location matching the given query and
    returns the 3 day forecast for the location.'''
    pass
