import requests # http://python-requests.org/

URL = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php'

params = {
    'lat': '39',
    'lon': '-77',
    'product': 'time-series',
    'sky': 'sky',
    'maxt': 'maxt',
    'mint': 'mint',
}

resp = requests.get(URL, params=params)

# Now you get to extract data from the XML response
print resp.text