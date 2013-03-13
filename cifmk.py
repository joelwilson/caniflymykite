import os
from flask import Flask, render_template, abort, request, url_for, redirect, \
    send_from_directory

import noaa
import utils
import geonames as gn
from weather import Weather


app = Flask(__name__)
DEBUG = False if os.environ['CIFMK_DEBUG'].upper() == 'FALSE' else True


@app.route('/')
def index():
    '''Returns the page for the index/landing page.'''
    featured_places = [{'name': 'San Francisco', 'lat': 37.77, 'lon': -122.419},
                       {'name': 'Santa Monica', 'lat': 34.01, 'lon': -118.49},
                       {'name': 'Seattle', 'lat': 47.606, 'lon': -122.33}]
    for place in featured_places:
        weather = Weather(place['lat'], place['lon'])
        place['wind_speed'] = weather['wind_speed']
        place['temperature'] = weather['temperature']
        place['canfly'] = weather['canfly']
    return render_template('index.html', featured_places=featured_places)


@app.route('/weather', methods=['GET'])
def weather():
    if not request.args:
        abort(404)
    if request.args.__contains__('lat') and request.args.__contains__('lon'):
        weather = Weather(request.args['lat'], request.args['lon'])
    elif request.args['location']:
        try:
            place = gn.search(request.args['location'].strip())[0]
        except IndexError: # no search results
            abort(404)
        weather = Weather(place['lat'], place['lng'])
    if weather is not None:
        return render_template('weather.html', **weather.elements)
    else:
        abort(404)


@app.route('/about')
def about():
    '''Returns the rendered about page.'''
    return render_template('about.html')


@app.route('/kites')
def kites():
    '''Returns the rendered "Kites We Like" page.'''
    return render_template('kites.html')

    
@app.route('/blog')
def blog():
    '''Returns the URL for the blog.'''
    return redirect('', code=301)


@app.route('/newsletter')
def newsletter():
    return render_template('newsletter.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/sitemap.xml')
@app.route('/robots.txt')
def static_from_root():
    '''Sends the file in the route from the static folder to the browser.'''
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
