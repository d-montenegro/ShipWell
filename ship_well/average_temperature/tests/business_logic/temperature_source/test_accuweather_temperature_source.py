from pytest import (
    mark,
    raises,
)

from average_temperature.business_logic.temperature_source.sources import AccuweatherTemperatureSource
from average_temperature.business_logic.temperature_source.exceptions import (
    TemperatureSourceUnexpectedStatusCode,
    TemperatureSourceException,
)


def test_temperature_successfully_retrieved(requests_mock_get):
    """
    Check that the request to Accuweather service is properly build and the current temperature
    is successfully retrieved
    """
    get, response = requests_mock_get
    response.status_code = 200
    response.json = lambda: {
        'simpleforecast': {
            'forecastday': [{
                'current': {
                    'fahrenheit': '55',
                    'celsius': '12'
                },
                'icon_url': 'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
                'period': 1,
                'pop': 0,
                'skyicon': 'mostlysunny',
                'high': {
                    'fahrenheit': '68',
                    'celsius': '20'
                },
                'qpf_allday': {
                    'mm': 0.0,
                    'in': 0.0
                },
                'low': {
                    'fahrenheit': '50',
                    'celsius': '10'
                },
                'conditions': 'Partly Cloudy',
                'icon': 'partlycloudy'
            }]
        }
    }

    current_temperature = AccuweatherTemperatureSource.get_current_temperature(1.0, 2.0)

    # check the current temperature is successfully retrieved
    assert current_temperature == 12.0

    # check the request is made properly
    get.assert_called_with(AccuweatherTemperatureSource.BASE_URL, params={'latitude': 1.0, 'longitude': 2.0})


@mark.parametrize('status_code', [500, 400, 404])
def test_unexpected_status_code(requests_mock_get, status_code):
    """
    Check that the corresponding exception is raised if the status code in the response is unexpected
    """
    _, response = requests_mock_get
    response.status_code = status_code
    response.text = 'This is a dummy text'

    with raises(TemperatureSourceUnexpectedStatusCode) as exc_info:
        AccuweatherTemperatureSource.get_current_temperature(1.0, 2.0)

    exc = exc_info.value
    assert exc.response == response.text


@mark.parametrize('invalid_response', [
    None,
    'Sample String',  # Non dict response
    {'foo': 'bar'},  # missing 'simpleforecast' key
    {'simpleforecast': {'for', 'bar'}},  # missing 'forecastday' key
    {'simpleforecast': {'forecastday': 'foo'}},  # missing 'forecast' value not list
    {'simpleforecast': {'forecastday': []}},  # missing 'forecast' empty list
    {'simpleforecast': {'forecastday': [{'for': 'bar'}]}},  # missing 'current' key
    {'simpleforecast': {'forecastday': [{'current': {'foo': 'bar'}}]}},  # missing 'celsius' key
])
def test_unexpected_response(requests_mock_get, invalid_response):
    """
    Check that the corresponding exception is raised if the response body is unexpected
    """
    _, response = requests_mock_get
    response.status_code = 200
    response.json = lambda: invalid_response

    with raises(TemperatureSourceException):
        AccuweatherTemperatureSource.get_current_temperature(1.0, 2.0)
