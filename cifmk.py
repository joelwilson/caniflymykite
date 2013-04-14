import os
from flask import Flask, render_template, abort, request, redirect, \
                  send_from_directory

import weather
import kites
import noaa


APP = Flask(__name__)
DEBUG = False if os.environ['CIFMK_DEBUG'].upper() == 'FALSE' else True
KITES = kites.get_kites()


@APP.route('/')
def index():
    '''Returns the page for the index/landing page.'''
    featured_places = [
        {'name': 'San Francisco', 'query': 'San Francisco, CA'},
        {'name': 'Santa Monica', 'query': 'Santa Monica, CA'},
        {'name': 'Seattle, WA', 'query': 'Seattle, WA'}
    ]
    for place in featured_places:
        place_weather = weather.Weather(place['query'])
        place['wind_speed'] = place_weather['wind_mph']
        place['temperature'] = place_weather['temp_f']
        place['canfly'] = place_weather['canfly']
    return render_template('index.html', featured_places=featured_places)


@APP.route('/weather', methods=['GET'])
def get_weather():
    '''Render the page for the passed http location parameters.
    
    Accepted parameters
    location: query/search text for a location'''
    if not request.args:
        abort(404)
    if request.args['location']:
        try:
            weather_info = weather.Weather(request.args['location'])
        except weather.WeatherError:
            abort(404)
    return render_template('weather.html', **weather_info.elements)


@APP.route('/about')
def about():
    '''Returns the rendered about page.'''
    return render_template('about.html')


@APP.route('/kites')
def kites_we_like():
    '''Returns the rendered "Kites We Like" page.'''
    return render_template('kites.html', kites=KITES)

    
@APP.route('/blog')
def blog():
    '''Returns the URL for the blog.'''
    return redirect('', code=301)


@APP.route('/newsletter')
def newsletter():
    '''Returns the newsletter page.'''
    return render_template('newsletter.html')


@APP.errorhandler(404)
def page_not_found(error):
    '''Displays the custom 404 page.'''
    return render_template('404.html'), 404


@APP.route('/sitemap.xml')
@APP.route('/robots.txt')
def static_from_root():
    '''Sends the file in the route from the static folder to the browser.'''
    return send_from_directory(APP.static_folder, request.path[1:])


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    APP.run(host='0.0.0.0', port=PORT, debug=DEBUG)
