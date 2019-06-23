"""
This module isolates the logic to retrieve current temperature from noaa
"""

import logging
from urllib.parse import urljoin

import requests

from . import register_weather_source
from .constants import (
    STATUS_CODE_SUCCESS,
    MOCK_API_URL,
)
from .exceptions import NoaaInvalidRequest

logger = logging.getLogger(__name__)


@register_weather_source('noaa')
def get_current_temperature(latitude: float, longitude: float) -> float:
    """
    Retrieve the current temperature from Noaa.

    :param latitude: the desired latitude
    :param longitude: the desired longitude

    :return: the current temperature in celsius grades
    :raises AccuweatherRequestFailed if there are communication issues with accuweather
    """
    payload = {'latlon': ','.join([str(latitude), str(longitude)])}

    accuweather_url = urljoin(MOCK_API_URL, 'noaa')
    response = requests.get(accuweather_url, params=payload)
    if response.status_code == STATUS_CODE_SUCCESS:
        return _retrieve_current_weather(response.json())
    else:
        raise NoaaInvalidRequest(response.text)


def _retrieve_current_weather(json_response: dict) -> float:
    """
    Parse and retrieve current temperature from noaa response

    The response looks like this:

    {
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

    :param json_response: the json response from noaa
    :return: the current temperature in celsius grades
    """
    current_weather = json_response['today']['current']
    return float(current_weather["celsius"])
