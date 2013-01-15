import os
from flask import Flask, render_template, abort, request, url_for, redirect

from noaa import get_weather, tomph, heading, WeatherError, iszip

app = Flask(__name__)


@app.route('/')
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
        'wind_speed': tomph(weather.val('wind_speed')),
        'wind_dir': heading(weather.val('wind_dir')),
        'rain_chance': weather.val('rain_prob'),
        'location': zipcode,
        'current_temp': weather.val('temperature')
    }
    return render_template('index.html', **args)


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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
