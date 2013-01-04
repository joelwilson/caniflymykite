import os
from flask import Flask, render_template, abort

from noaa import get_weather, tomph, WeatherError

app = Flask(__name__)

@app.route('/')
@app.route('/zip/<zipcode>')
@app.route('/<zipcode>')
def main(zipcode=95382):
    try:
        w = get_weather(zipcode)
        print w
    except WeatherError:
        abort(404)
    args = {
        'wind_speed': tomph(w.val('wind_speed')),
        'wind_dir': w.val('wind_dir'),
        'rain_chance': w.val('rain_prob'),
        'location': zipcode,
        'current_temp': w.val('temperature')
    }
    return render_template('index.html', **args)


    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)