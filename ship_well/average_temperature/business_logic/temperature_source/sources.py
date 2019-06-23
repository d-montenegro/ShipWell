"""
This module isolates all the logic to retrieve current temperature from all allowed sources.
"""
from abc import ABC, abstractmethod
import logging
from urllib.parse import urljoin

import requests
from requests.exceptions import ConnectionError

from .constants import (
    MOCK_API_URL,
    NOAA_SOURCE_NAME,
    ACCUWEATHER_SOURCE_NAME,
    WEATHER_DOT_COM_SOURCE_NAME,
)

from .utils import translate_from_farenheit_to_celsius

from .exceptions import (
    TemperatureSourceException,
    TemperatureSourceConnectionError,
    TemperatureSourceUnexpectedResponse,
    TemperatureSourceUnexpectedStatusCode
)

logger = logging.getLogger(__name__)


class WebAppTemperatureSource(ABC):
    """
    Abstract class to perform the retrieval of current temperature from web apps.

    There must be one implementation of this class by every source to retrieve current temperature from
    """
    ID = None  # it's an identifier for the source
    BASE_URL = None  # the web app URL
    VERB = None  # the HTTP verb to call

    RESPONSE_EXPECTED_STATUS_CODE = [200]   # list of the allowed HTTP ERROR CODE expected to get in the response

    @classmethod
    def get_current_temperature(cls, latitude: float, longitude: float) -> float:
        """
        Get the current temperature in celsius grades

        This method uses the implementation of the abstract methods to actually perform a request an obtain from
        its response the current temperature

        :param latitude: the desired latitude
        :param longitude: the desired longitude
        :return the current temperature in celsius degrees
        :raise TemperatureSourceException the temperature can't be retrieved
        """
        func = getattr(requests, cls.VERB)
        payload = cls._get_payload(latitude, longitude)

        try:
            response = func(cls.BASE_URL, **payload)
        except ConnectionError:
            # Could not get to the source
            raise TemperatureSourceConnectionError('Could not connect to source {}'.format(cls.ID))
        else:
            # check if the http status code is one of the expected, parse the response
            if response.status_code in cls.RESPONSE_EXPECTED_STATUS_CODE:
                try:
                    return cls._parse_response(response)
                except TemperatureSourceException:
                    # it's one of the expected exception this class must raise. Logging it an re-raise
                    logger.exception('Could not retrieve current temperature from %s', cls.ID)
                    raise
                except Exception:
                    # it's an unexpected exception. Log it and raise the base exception
                    logger.exception('Unknown error while parsing response from %s. Response %s',
                                     cls.ID,
                                     response.text)
                    raise TemperatureSourceException('Could not retrieve current temperature from %s', cls.ID)
            else:
                # The status code is unexpected... Raise the corresponding exception
                raise TemperatureSourceUnexpectedStatusCode(response.text)

    @classmethod
    def from_source_name(cls, source_name: str):
        """
        Factory to get the corresponding subclass by its identifier

        :param source_name: the desired source
        :return: the corresponding class
        :raises TemperatureSourceUnexpectedStatusCode if there's no implementation for the given name
        """
        try:
            return WEATHER_SOURCE[source_name]
        except KeyError:
            raise TemperatureSourceException('Invalid source {}'.format(source_name))

    @classmethod
    @abstractmethod
    def _get_payload(cls, latitude: float, longitude: float) -> dict:
        """
        This method must be implemented by subclasses to create the payload for the request
        :param latitude: the desired latitude
        :param longitude: the desired longitude
        :return: the payload to make the request
        """
        pass

    @classmethod
    @abstractmethod
    def _parse_response(cls, response) -> float:
        """
        This method must extract the current temperature from the response
        :param response: the HTTP response
        :return: the curent temperature in celsius grades
        :raises TemperatureSourceException on parsing errors
        """
        pass


class NoaaTemperatureSource(WebAppTemperatureSource):
    """
    This class performs the current temperature retrieval from Noaa
    """
    ID = NOAA_SOURCE_NAME
    BASE_URL = urljoin(MOCK_API_URL, NOAA_SOURCE_NAME)
    VERB = 'get'

    @classmethod
    def _get_payload(cls, latitude, longitude):
        return {
            'params':
                {
                    'latlon': ','.join([str(latitude), str(longitude)])
                }
        }

    @classmethod
    def _parse_response(cls, response):
        """
        Parse and retrieve current temperature from response

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

        :param response: the json response from noaa
        :return: the current temperature in celsius grades
        """
        current_weather = response.json()['today']['current']
        return float(current_weather["celsius"])


class AccuweatherTemperatureSource(WebAppTemperatureSource):
    """
    This class performs the current temperature retrieval from AccuWeather
    """
    ID = ACCUWEATHER_SOURCE_NAME
    BASE_URL = urljoin(MOCK_API_URL, ACCUWEATHER_SOURCE_NAME)
    VERB = 'get'

    @classmethod
    def _get_payload(cls, latitude, longitude):
        return {
            'params':
                {
                    'latitude': latitude,
                    'longitude': longitude
                }
        }

    @classmethod
    def _parse_response(cls, response):
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

        :param response: the response from accuweather
        :return: the current temperature in celsius grades
        :raises TemperatureSourceUnexpectedResponse if the response can't be parsed successfully
        """
        json_response = response.json()
        forecastday = json_response['simpleforecast']['forecastday']
        if len(forecastday) != 1:
            raise TemperatureSourceUnexpectedResponse(json_response,
                                                      'Response contains more {} entries for forecastday'.format(
                                                          len(forecastday)))
        else:
            current_weather = forecastday[0]['current']
            return float(current_weather["celsius"])


class WeatherDotComTemperatureSource(WebAppTemperatureSource):
    """
    This class performs the current temperature retrieval from weather.com
    """
    ID = WEATHER_DOT_COM_SOURCE_NAME
    BASE_URL = urljoin(MOCK_API_URL, 'weatherdotcom')
    VERB = 'post'

    @classmethod
    def _get_payload(cls, latitude, longitude):
        return {
            'json':
                {
                    "lat": latitude,
                    "lon": longitude
                }
        }

    @classmethod
    def _parse_response(cls, response):
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
        :param response: the response from weather.com
        :return: the current temperature in celsius grades
        :raises TemperatureSourceUnexpectedResponse if the response can't be parsed
        """
        # success
        json_response = response.json()
        query = json_response['query']
        if query['count'] != 1:
            raise TemperatureSourceUnexpectedResponse(json_response, 'Found multiple results in weather.com response')
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
                raise TemperatureSourceUnexpectedResponse(json_response, 'Unknown temperature unit {}'.format(unit))


WEATHER_SOURCE = {cls.ID: cls for cls in WebAppTemperatureSource.__subclasses__()}
