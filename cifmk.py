import os
from flask import Flask, render_template, abort, request, url_for, redirect, \
    flash

from noaa import get_weather, tomph, heading, WeatherError, iszip

app = Flask(__name__)


@app.route('/')
@app.route('/zip/<zipcode>')
def get_by_zip(zipcode=95382):
    if not iszip(zipcode):
        # ADD ERROR HANDLING
        # http://flask.pocoo.org/docs/patterns/flashing/#message-flashing-pattern
        zipcode=95382
    try:
        w = get_weather(zipcode)
    except WeatherError:
        abort(404)
    args = {
        'wind_speed': tomph(w.val('wind_speed')),
        'wind_dir': heading(w.val('wind_dir')),
        'rain_chance': w.val('rain_prob'),
        'location': zipcode,
        'current_temp': w.val('temperature')
    }
    return render_template('index.html', **args)


@app.route('/get_weather/', methods=['GET'])
def weather_from_form():
    return redirect(url_for('get_by_zip', 
                            zipcode=request.args.get('location')))

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)