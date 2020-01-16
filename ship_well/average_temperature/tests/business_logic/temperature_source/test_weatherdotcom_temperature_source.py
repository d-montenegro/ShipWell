from pytest import (
    mark,
    raises,
)

from average_temperature.business_logic.temperature_source.sources import WeatherDotComTemperatureSource
from average_temperature.business_logic.temperature_source.exceptions import (
    TemperatureSourceUnexpectedStatusCode,
    TemperatureSourceException,
)


def test_temperature_successfully_retrieved(requests_mock_post):
    """
    Check that the request to WeatherDotCom service is properly build and the current temperature
    is successfully retrieved
    """
    post, response = requests_mock_post
    response.status_code = 200
    response.json = lambda: {
        'query': {
            'count': 1,
            'lang': 'en-US',
            'results': {
                'channel': {
                    'lastBuildDate': 'Thu, 21 Sep 2017 09:00 AM AKDT',
                    'atmosphere': {
                        'pressure': '1014.0',
                        'rising': '0',
                        'visibility': '16.1',
                        'humidity': '80'
                    },
                    'description': 'Current Weather',
                    'language': 'en-us',
                    'item': {
                        'lat': '64.499474',
                        'guid': {
                            'isPermaLink': 'false'
                        },
                        'pubDate': 'Thu, 21 Sep 2017 08:00 AM AKDT',
                        'long': '-165.405792',
                        'title': 'Conditions for Nome, AK, US at 08:00 AM AKDT'
                    },
                    'ttl': '60',
                    'units': {
                        'temperature': 'C'
                    },
                    'astronomy': {
                        'sunset': '9:6 pm',
                        'sunrise': '8:42 am'
                    },
                    'condition': {
                        'date': 'Thu, 21 Sep 2017 08:00 AM AKDT',
                        'text': 'Mostly Clear',
                        'code': '33',
                        'temp': '37'
                    }
                }
            },
            'created': '2017-09-21T17:00:22Z'
        }
    }

    current_temperature = WeatherDotComTemperatureSource.get_current_temperature(1.0, 2.0)

    # check the current temperature is successfully retrieved
    assert current_temperature == 37.0

    # check the request is made properly
    post.assert_called_with(WeatherDotComTemperatureSource.BASE_URL, json={'lat': 1.0, 'lon': 2.0})


def test_temperature_successfully_retrieved_fahrenheit_conversion(requests_mock_post):
    """
    Check that the request to WeatherDotCom service is properly build and the current temperature
    is successfully retrieved and translated from fahrenheit to celsius
    """
    post, response = requests_mock_post
    response.status_code = 200
    response.json = lambda: {
        'query': {
            'count': 1,
            'lang': 'en-US',
            'results': {
                'channel': {
                    'lastBuildDate': 'Thu, 21 Sep 2017 09:00 AM AKDT',
                    'atmosphere': {
                        'pressure': '1014.0',
                        'rising': '0',
                        'visibility': '16.1',
                        'humidity': '80'
                    },
                    'description': 'Current Weather',
                    'language': 'en-us',
                    'item': {
                        'lat': '64.499474',
                        'guid': {
                            'isPermaLink': 'false'
                        },
                        'pubDate': 'Thu, 21 Sep 2017 08:00 AM AKDT',
                        'long': '-165.405792',
                        'title': 'Conditions for Nome, AK, US at 08:00 AM AKDT'
                    },
                    'ttl': '60',
                    'units': {
                        'temperature': 'F'
                    },
                    'astronomy': {
                        'sunset': '9:6 pm',
                        'sunrise': '8:42 am'
                    },
                    'condition': {
                        'date': 'Thu, 21 Sep 2017 08:00 AM AKDT',
                        'text': 'Mostly Clear',
                        'code': '33',
                        'temp': '90'
                    }
                }
            },
            'created': '2017-09-21T17:00:22Z'
        }
    }

    current_temperature = WeatherDotComTemperatureSource.get_current_temperature(1.0, 2.0)

    # check the current temperature is successfully retrieved
    assert current_temperature == (90 - 32) * 5./9.

    # check the request is made properly
    post.assert_called_with(WeatherDotComTemperatureSource.BASE_URL, json={'lat': 1.0, 'lon': 2.0})


@mark.parametrize('status_code', [500, 400, 404])
def test_unexpected_status_code(requests_mock_post, status_code):
    """
    Check that the corresponding exception is raised if the status code in the response is unexpected
    """
    _, response = requests_mock_post
    response.status_code = status_code
    response.text = 'This is a dummy text'

    with raises(TemperatureSourceUnexpectedStatusCode) as exc_info:
        WeatherDotComTemperatureSource.get_current_temperature(1.0, 2.0)

    exc = exc_info.value
    assert exc.response == response.text


@mark.parametrize('invalid_response', [
    None,
    'Sample String',  # Non dict response
    {'foo': 'bar'},  # missing 'query' key
    {'query': {'count': 0}},  # query does not retrieve any result
    {'query': {'count': 10}},  # query retrieves multiple results
    {'query': {'count': 1, 'results': {}}},  # missing 'channel' key
    {'query': {'count': 1, 'results': {'channel': {}}}},  # missing 'units' key
    {'query': {'count': 1, 'results': {'channel': {'units': {}}}}},  # missing 'temperature' key
    {'query': {'count': 1, 'results': {'channel': {'units': {'temperature': 'A'}}}}},  # invalid temperature unit
    {'query': {'count': 1, 'results': {'channel': {'units': {'temperature': 'C'}}}}},  # missing 'condition' key
    # missing 'temp' key
    {'query': {'count': 1, 'results': {'channel': {'units': {'temperature': 'C'}, 'condition': {}}}}},
    # invalid temperature
    {'query': {'count': 1, 'results': {'channel': {'units': {'temperature': 'C'}, 'condition': {'temp': 'AA'}}}}},
])
def test_unexpected_response(requests_mock_post, invalid_response):
    """
    Check that the corresponding exception is raised if the response body is unexpected
    """
    _, response = requests_mock_post
    response.status_code = 200
    response.json = lambda: invalid_response

    with raises(TemperatureSourceException):
        WeatherDotComTemperatureSource.get_current_temperature(1.0, 2.0)
