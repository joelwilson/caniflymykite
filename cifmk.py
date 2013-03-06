import os
from flask import Flask, render_template, abort, request, url_for, redirect, \
    send_from_directory

import noaa
import utils
import geonames as gn
from weather import Weather


app = Flask(__name__)
DEBUG = False if os.environ['CIFMK_DEBUG'] == 'False' else True


@app.route('/')
def index():
    '''Returns the page for the index/landing page.'''
    featured_places = ['San Francisco', 'lat': 37.77, 'lon': -122.419},
                       {'name': 'Santa Monica', 'lat': 34.01, 'lon': -118.49},
                       {'name': 'Seattle', 'lat': 47.606, 'lon': -122.33}]
    for place in featured_places:
        fc = noaa.forecast(place['lat'], place['lon'])
        cw = gn.weather(place['lat'], place['lon'])
        place['wind_speed'] = utils.tomph(cw['windSpeed'])
        place['temperature'] = utils.ctof(cw['temperature'])
        place['canfly'] = noaa.canfly(cw['windSpeed'],
                                      int(fc.get('rain_prob')),
                                      cw['temperature'])
    return render_template('index.html', featured_places=featured_places)


@app.route('/zip/<zipcode>/')
def get_by_zip(zipcode=95382):
    '''Returns a page for a specific zip code, displaying weather info.'''
    if not noaa.iszip(zipcode):
        return render_template('error.html', msg="Invalid zip code")
    try:
        fc = noaa.get_forecast(zipcode)
        cw = gn.weather(fc.latlon[0], fc.latlon[1])
    except noaa.WeatherError:
        abort(404)
    args = {
        'rain_chance': int(fc.get('rain_prob', debug=DEBUG)),
        'zipcode': zipcode}
    if cw is not None:
        args['wind_speed'] = utils.tomph(cw['windSpeed'])
        try:
            args['wind_dir'] = utils.heading(cw['windDirection'])
        except KeyError:
            args['wind_dir'] = utils.heading(fc.get('wind_dir', debug=DEBUG))
        args['temperature'] = utils.ctof(cw['temperature'])
    else:
        args['wind_speed'] = utils.tomph(fc.get('wind_speed', debug=DEBUG))
        args['wind_dir'] = utils.heading(fc.get('wind_dir', debug=DEBUG))
        args['temperature'] = fc.get('temperature', debug=DEBUG)
    args['canfly'] = noaa.canfly(args['wind_speed'],
                                 args['rain_chance'],
                                 args['temperature'])
    return render_template('weather.html', **args)


@app.route('/location', methods=['GET'])
def location():
    if not request.args:
        abort(404)
    if request.args['lat'] and request.args['lon']:
        place['weather'] = Weather(request.args['lat'], request.args['lon'])
    if request.args['q']:
        place = gn.search(request.args['q'].strip())[0]
        place['weather'] = Weather(place['lat'], place['lng'])
    return render_template('test.html', place=place)

@app.route('/get_weather/', methods=['GET'])
def weather_from_form():
    '''Extracts the user provided zip code from the form data and redirects
    to the appropriate zip code page.
    '''
    param = request.args.get('form_location')
    try:
        int(param)
        return redirect(url_for('get_by_zip',
                                zipcode=param),
                        code=301)
    except ValueError:
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
