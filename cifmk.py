import os
from flask import Flask, render_template, abort, request, url_for, redirect, \
    send_from_directory

from noaa import get_weather, tomph, heading, WeatherError, iszip, canfly

app = Flask(__name__)
DEBUG = True


@app.route('/')
@app.route('/index')
def index():
    '''Returns the page for the root/landing page.'''
    return render_template('index.html')

@app.route('/zip/<zipcode>/')
def get_by_zip(zipcode=95382):
    '''Returns a page for a specific zip code, displaying wind speed, etc.'''
    if not iszip(zipcode):
        return render_template('error.html', msg="Invalid zip code")
    try:
        weather = get_weather(zipcode)
    except WeatherError:
        abort(404)
    args = {
        'wind_speed': tomph(weather.val('wind_speed', debug=DEBUG)),
        'wind_dir': heading(weather.val('wind_dir', debug=DEBUG)),
        'rain_chance': int(weather.val('rain_prob', debug=DEBUG)),
        'location': zipcode,
        'current_temp': weather.val('temperature', debug=DEBUG)
    }
    print args
    args['canfly'] = canfly(args['wind_speed'], 
                            args['rain_chance'],
                            args['current_temp'])
    return render_template('weather.html', **args)


@app.route('/get_weather/', methods=['GET'])
def weather_from_form():
    '''Extracts the user provided zip code from the form data and redirects
    to the appropriate zip code page.
    '''
    return redirect(url_for('get_by_zip',
                            zipcode=request.args.get('form_location')))


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
    return redirect('')


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
