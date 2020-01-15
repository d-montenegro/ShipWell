import requests
from unittest.mock import MagicMock

from pytest import (
    fixture,
    mark,
    raises,
)

from average_temperature.business_logic.temperature_source.sources import NoaaTemperatureSource
from average_temperature.business_logic.temperature_source.exceptions import (
    TemperatureSourceUnexpectedStatusCode,
    TemperatureSourceException,
)


@fixture
def requests_mock(monkeypatch):
    response = MagicMock()
    get = MagicMock(return_value=response)
    monkeypatch.setattr(requests, "get", get)
    return get, response


def test_temperature_successfully_retrieved(requests_mock):
    """
    Check that the request to Noaa service is properly build and the current temperature
    is successfully retrieved
    """
    get, response = requests_mock
    response.status_code = 200
    response.json = lambda: {
        'today': {
            'high': {
                'fahrenheit': '68',
                'celsius': '20'
            },
            'current': {
                'fahrenheit': '55',
                'celsius': '12'
            },
            'low': {
                'fahrenheit': '50',
                'celsius': '10'
            }
        }
    }

    current_temperature = NoaaTemperatureSource.get_current_temperature(1.0, 2.0)

    # check the current temperature is successfully retrieved
    assert current_temperature == 12.0

    # check the request is made properly
    get.assert_called_with(NoaaTemperatureSource.BASE_URL, params={'latlon': '1.0,2.0'})


@mark.parametrize('status_code', [500, 400, 404])
def test_unexpected_status_code(requests_mock, status_code):
    """
    Check that the corresponding exception is raised if the status code in the response is unexpected
    """
    _, response = requests_mock
    response.status_code = status_code
    response.text = 'This is a dummy text'

    with raises(TemperatureSourceUnexpectedStatusCode) as exc_info:
        NoaaTemperatureSource.get_current_temperature(1.0, 2.0)

    exc = exc_info.value
    assert exc.response == response.text


@mark.parametrize('invalid_response', [
    None,
    'Sample String',  # Non dict response
    {'foo': 'bar'},  # missing 'today' key
    {'today': {'for', 'bar'}},  # missing 'current' key
    {'today': {'current': {'foo': 'bar'}}},  # missing 'celcius' key
])
def test_unexpected_response(requests_mock, invalid_response):
    """
    Check that the corresponding exception is raised if the response body is unexpected
    """
    _, response = requests_mock
    response.status_code = 200
    response.json = lambda: invalid_response

    with raises(TemperatureSourceException):
        NoaaTemperatureSource.get_current_temperature(1.0, 2.0)
