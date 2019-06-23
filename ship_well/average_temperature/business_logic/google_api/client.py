"""
This modules provides a client to communicate with Google Maps API

Source: https://developers.google.com/maps/documentation/geocoding/start
"""
import logging
from typing import Tuple

import requests
from requests.exceptions import ConnectionError

from .exceptions import (
    GoogleAPIConnectionError,
    GoogleAPIUnexpectedResponse,
    GoogleAPIUnexpectedStatusCode,
)


logger = logging.getLogger(__name__)


class GoogleApiClient:
    """
    This class contains the internals to communicate with Google Maps API
    """

    GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    STATUS_CODE_SUCCESS = 200
    STATUS_OK = "OK"

    def __init__(self, api_key: str):
        """
        :param api_key: a valid Google API KEY to communicate with Google Maps API
        """
        self.key = api_key

    def get_location_from_zip_code(self, zip_code: str) -> Tuple[float, float]:
        """
        Get latitude - longitude coordinates from zip code

        :param zip_code: the desired zip code
        :return: the latitude - longitude coordinates that corresponds to the given zip code, or None
        if there's no location for the given zip code
        :raises GeoCodeException if the coordinates can't be retrieved
        """
        payload = {
            "key": self.key,
            "components": 'postal_code:{}'.format(zip_code)
        }

        response = self._get(payload)

        if response.status_code == self.STATUS_CODE_SUCCESS:
            json_response = response.json()
            self._verify_status(json_response)

            results = json_response['results']
            if len(results) == 0:
                logger.error('There are not results for the zip code {}. Response: {}'.format(
                    zip_code, response.text
                ))
                return None  # the zip code is not valid
            else:
                result = results[0]
                location = result['geometry']['location']
                return float(location['lat']), float(location['lng'])
        else:
            logger.error('Failed to retrieve location from postal code. '
                         'Status code: {r.status_code} - text: {r.text}'.format(r=response))
            raise GoogleAPIUnexpectedStatusCode(response)

    def check_coordinates_validity(self, latitude: float, longitude: float) -> bool:
        """
        Check latitude and longitude coordinates are valid

        :param latitude: the desired latitude
        :param longitude: the desired longitude
        :return True if coordinates are valid. False otherwise

        :raises GeoCodeServiceUnexpectedResponse on communication issues
        """
        payload = {
            "key": self.key,
            "latlng": ','.join([str(latitude), str(longitude)])
        }

        response = self._get(payload)

        if response.status_code == self.STATUS_CODE_SUCCESS:
            json_response = response.json()
            self._verify_status(json_response)
            results = json_response['results']
            return len(results) != 0

        else:
            logger.error('Failed to retrieve location from postal code. '
                         'Status code: {r.status_code} - text: {r.text}'.format(r=response))
            raise GoogleAPIUnexpectedStatusCode(response)

    def _get(self, payload: dict):
        """
        Perform a GET on Google Maps API

        :param payload: the query
        :return: the corresponding response
        :raises GeoCodeServiceConnectionError on connection errors
        """
        try:
            return requests.get(self.GOOGLE_MAPS_API_URL, params=payload)
        except ConnectionError:
            raise GoogleAPIConnectionError('Google Maps API is down')

    @classmethod
    def _verify_status(cls, json_response: dict) -> None:
        """
        Check status code if "OK" in the api's json response

        :param json_response: api's json response
        :raise GoogleAPIUnexpectedResponse if the status is not "OK"
        """
        status = json_response['status']
        if status != cls.STATUS_OK:
            logger.error("Google Maps API is not available by the moment. Response %s", json_response)
            raise GoogleAPIUnexpectedResponse(json_response,
                                              'The status reported by google API is {}'.format(status))
