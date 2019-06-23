"""
This module isolates the logic to retrieve current temperature from AccuWeather
"""
import logging
from urllib.parse import urljoin

import requests

from . import register_weather_source
from .constants import (
    MOCK_API_URL,
    STATUS_CODE_SUCCESS,
)
from .exceptions import (
    AccuweatherInvalidRequest,
    AccuweatherUnexpectedResponse,
)

logger = logging.getLogger(__name__)


@register_weather_source('accuweather')
def get_current_temperature(latitude: float, longitude: float) -> float:
    """
    Retrieve the current temperature from AccuWeather.

    :param latitude: the desired latitude
    :param longitude: the desired longitude

    :return: the current temperature in celsius grades
    :raises AccuweatherRequestFailed if there are communication issues with accuweather
    """
    payload = {
        'latitude': latitude,
        'longitude': longitude
    }

    accuweather_url = urljoin(MOCK_API_URL, 'accuweather')
    response = requests.get(accuweather_url, params=payload)
    if response.status_code == STATUS_CODE_SUCCESS:
        return _retrieve_current_weather(response.json())
    else:
        raise AccuweatherInvalidRequest(response.text)


def _retrieve_current_weather(json_response: dict) -> float:
    """
    Parse and retrieve current temperature from accuweather response

    The accuweather response looks like this:

    {
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

    :param json_response: the json response from accuweather
    :return: the current temperature in celsius grades
    :raises AccuweatherUnexpectedResponse if the response can't be parsed successfully
    """
    forecastday = json_response['simpleforecast']['forecastday']
    if len(forecastday) != 1:
        raise AccuweatherUnexpectedResponse('Response contains more {} entries for forecastday'.format(
            len(forecastday)))
    else:
        current_weather = forecastday[0]['current']
        return float(current_weather["celsius"])
