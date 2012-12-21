import os
from flask import Flask, render_template

from noaa import get_weather, mph

app = Flask(__name__)

@app.route('/')
@app.route('/zip/<zipcode>')
@app.route('/<zipcode>')
def main(zipcode=95382):
    w = get_weather(zipcode)
    args = {
        'wind_speed': mph(w.val('wind_speed')),
        'wind_dir': w.val('wind_dir'),
        'rain_chance': w.val('rain_prob'),
        'location': zipcode,
        'current_temp': w.val('temperature')
    }
    return render_template('index.html', **args)

@app.route('/zip/<zipcode>/')
def show_weather(zipcode):
    return 'Hello %s!' % zipcode
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)