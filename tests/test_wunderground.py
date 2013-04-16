from nose.tools import *

import wunderground


class TestWunderground():
    def test_current_conditions_turlock(self):
        current = wunderground.current_conditions('Turlock, CA')
        assert_equals(
            current['current_observation']['display_location']['city'],
            'Turlock'
        )

    def test_forecast_Turlock_low(self):
        forecast = wunderground.forecast('Turlock')
        assert_in(
            'low',
            forecast['forecast']['simpleforecast']['forecastday'][0].keys()
        )
