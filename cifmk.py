import os
from flask import Flask, render_template, abort, request, url_for, redirect, \
    send_from_directory

from noaa import get_forecast, tomph, heading, ForecastError, iszip, canfly, \
    ctof
import geonames as gn


app = Flask(__name__)
DEBUG = False if os.environ['CIFMK_DEBUG'] == 'False' else True


@app.route('/')
def index():
    '''Returns the page for the index/landing page.'''
    featured_places = [{'name': 'San Francisco', 'zip': 94103},
                       {'name': 'Santa Monica', 'zip': 90401},
                       {'name': 'Seattle', 'zip': 98101}]
    for place in featured_places:
        fc = get_forecast(place['zip'])
        cw = gn.weather(fc.latlon[0], fc.latlon[1])
        place['wind_speed'] = tomph(cw['windSpeed'])
        place['temperature'] = ctof(cw['temperature'])
        place['canfly'] = canfly(cw['windSpeed'],
                                 int(fc.val('rain_prob')),
                                 cw['temperature'])
    return render_template('index.html', featured_places=featured_places)


@app.route('/zip/<zipcode>/')
def get_by_zip(zipcode=95382):
    '''Returns a page for a specific zip code, displaying weather info.'''
    if not iszip(zipcode):
        return render_template('error.html', msg="Invalid zip code")
    try:
        fc = get_forecast(zipcode)
        cw = gn.weather(fc.latlon[0], fc.latlon[1])
    except ForecastError:
        abort(404)
    args = {
        'rain_chance': int(fc.val('rain_prob', debug=DEBUG)),
        'zipcode': zipcode}
    if cw is not None:
        args['wind_speed'] = tomph(cw['windSpeed'])
        try:
            args['wind_dir'] = heading(cw['windDirection'])
        except KeyError:
            args['wind_dir'] = heading(fc.val('wind_dir', debug=DEBUG))
        args['temperature'] = ctof(cw['temperature'])
    else:
        args['wind_speed'] = tomph(fc.val('wind_speed', debug=DEBUG))
        args['wind_dir'] = heading(fc.val('wind_dir', debug=DEBUG))
        args['temperature'] = fc.val('temperature', debug=DEBUG)
    args['canfly'] = canfly(args['wind_speed'],
                            args['rain_chance'],
                            args['temperature'])
    return render_template('weather.html', **args)


@app.route('/canfly', methods=['GET'])
def can_fly():
    lat = request.args.get('lat').strip()
    lon = request.args.get('lon').strip()


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
#@app.route('/favicon.ico')
def static_from_root():
    '''Sends the file in the route from the static folder to the browser.'''
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
