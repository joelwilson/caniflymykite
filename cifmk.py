import os

from flask import Flask, render_template, abort, request, redirect, \
                  send_from_directory

import weather
import kites
import noaa
import utils


app = Flask(__name__)
DEBUG = False if os.environ['CIFMK_DEBUG'].upper() == 'FALSE' else True
# these break Wunderground if in the query to the API
BAD_CHARS = ['.']
KITES = kites.get_kites()
KITE_CACHE = {}


@app.route('/')
def index():
    '''Returns the page for the index/landing page.'''
    global KITE_CACHE
    featured_places = [
        {'name': 'San Francisco', 'query': 'San Francisco, CA'},
        {'name': 'Santa Monica', 'query': 'Santa Monica, CA'},
        {'name': 'Seattle, WA', 'query': 'Seattle, WA'}
    ]
    for place in featured_places:
        # Do some wacky, messy cache thing for the front page so it doesn't
        # call the Wunderground API EVERY time the front page is loaded.
        query = place['query']
        max = 300 # 5 mins
        cache_keys = KITE_CACHE.keys()
        if query not in cache_keys or (query in keys and KITE_CACHE[query].age() > max):
            KITE_CACHE[query] = weather.Weather(
                utils.rem_chars(place['query'], BAD_CHARS)
            )
        place['wind_speed'] = KITE_CACHE[query]['wind_mph']
        place['temperature'] = KITE_CACHE[query]['temp_f']
        place['canfly'] = KITE_CACHE[query]['canfly']
    return render_template('index.html', featured_places=featured_places)


@app.route('/weather', methods=['GET'])
def get_weather():
    '''Render the page for the passed http location parameters.
    
    Accepted parameters
    location: query/search text for a location'''
    if not request.args:
        abort(404)
    if request.args['location']:
        try:
            weather_info = weather.Weather(
                utils.rem_chars(request.args['location'], BAD_CHARS)
            )
        except weather.WeatherError:
            abort(404)
    return render_template('weather.html', **weather_info.elements)


@app.route('/about')
def about():
    '''Returns the rendered about page.'''
    return render_template('about.html')


@app.route('/kites')
def kites_we_like():
    '''Returns the rendered "Kites We Like" page.'''
    return render_template('kites.html', kites=KITES)

    
@app.route('/blog')
def blog():
    '''Returns the URL for the blog.'''
    return redirect('', code=301)


@app.route('/newsletter')
def newsletter():
    '''Returns the newsletter page.'''
    return render_template('newsletter.html')


@app.errorhandler(404)
def page_not_found(error):
    '''Displays the custom 404 page.'''
    return render_template('404.html'), 404


@app.route('/sitemap.xml')
@app.route('/robots.txt')
def static_from_root():
    '''Sends the file in the route from the static folder to the browser.'''
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
