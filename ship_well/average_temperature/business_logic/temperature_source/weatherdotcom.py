"""
This module isolates the logic to retrieve current temperature from weather.com
"""

import logging
from urllib.parse import urljoin

import requests

from . import register_weather_source
from .utils import translate_from_farenheit_to_celsius
from .constants import (
    MOCK_API_URL,
    STATUS_CODE_SUCCESS,
)
from.exceptions import (
    WeatherDotComInvalidRequest,
    WeatherDotComUnexpectedResponse,
)

logger = logging.getLogger(__name__)


@register_weather_source('weather.com')
def get_current_temperature(latitude, longitude):
    """
    Retrieve the current temperature from weather.com

    :param latitude: the desired latitude
    :param longitude: the desired longitude

    :return: the current temperature in celsius grades
    :raises WeatherDotComRequestException if there are communication issues with accuweather
    """
    payload = {
        "lat": latitude,
        "lon": longitude
    }
    weatherdotcom_url = urljoin(MOCK_API_URL, 'weatherdotcom')
    response = requests.post(weatherdotcom_url, json=payload)
    if response.status_code == STATUS_CODE_SUCCESS:
        return _retrieve_current_weather(response.json())
    else:
        raise WeatherDotComInvalidRequest(response.text)


def _retrieve_current_weather(json_response: dict) -> float:
    """
    Parse and retrieve current temperature from accuweather response

    The accuweather response looks like this:

    {
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
                        'temp': '37'
                    }
                }
            },
            'created': '2017-09-21T17:00:22Z'
        }
    }
    :param json_response: the json response from accuweather
    :return: the current temperature in celsius grades
    :raises WeatherDotComUnexpectedResponse if the response can't be parsed
    """
    # success
    query = json_response['query']
    if query['count'] != 1:
        raise WeatherDotComUnexpectedResponse('Found multiple results in weather.com response')
    else:
        results = query['results']
        channel = results['channel']
        unit = channel['units']['temperature']
        temperature = float(channel['condition']['temp'])
        if unit == 'C':
            return temperature
        elif unit == 'F':
            return translate_from_farenheit_to_celsius(temperature)
        else:
            raise WeatherDotComUnexpectedResponse('Unknown temperature unit {}'.format(unit))
