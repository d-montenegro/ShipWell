"""
This modules provides a client to communicate with Google Maps API

Source: https://developers.google.com/maps/documentation/geocoding/start
"""
import logging
from typing import Tuple

import requests

from .exceptions import GeoCodeException


logger = logging.getLogger(__name__)


class GoogleApiClient:
    """
    This class contains the internals to communicate with Google Maps API
    """

    GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    STATUS_CODE_SUCCESS = 200

    def __init__(self, api_key: str):
        """
        :param api_key: a valid Google API KEY to communicate with Google Maps API
        """
        self.key = api_key

    def get_location_from_zip_code(self, zip_code: str) -> Tuple[float, float]:
        """
        Get latitude - longitude coordinates from zip code

        :param zip_code: the desired zip code
        :return: the latitude - longitude coordinates that corresponds to the given zip code
        :raises GeoCodeException if the coordinates can't be retrieved
        """
        payload = {
            "key": self.key,
            "components": 'postal_code:{}'.format(zip_code)
        }

        response = requests.get(self.GOOGLE_MAPS_API_URL, params=payload)
        if response.status_code == self.STATUS_CODE_SUCCESS:
            json_response = response.json()
            results = json_response['results']
            if len(results) != 1:
                logger.error('Could find a single result for postal code %s. Response: %s'.format(
                    zip_code, response.text
                ))
                raise GeoCodeException('Could not retrieve a unique coordinates')
            else:
                result = results[0]
                location = result['geometry']['location']
                return float(location['lat']), float(location['lng'])
        else:
            logger.error('Failed to retrieve location from postal code. '
                         'Status code: {r.status_code} - text: {r.text}'.format(r=response))
            raise GeoCodeException("Could not retrieve location")

    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Check latitude and longitude coordinates are valid

        :param latitude: the desired latitude
        :param longitude: the desired longitude
        :return: True if the coordinates are valid. False otherwise.
        """
        payload = {
            "key": self.key,
            "latlng": ','.join([str(latitude), str(longitude)])
        }

        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?', params=payload)
        if response.status_code == self.STATUS_CODE_SUCCESS:
            json_response = response.json()
            results = json_response['results']
            return len(results) == 1
        else:
            logger.warning('Failed to validate coordinates: lat {} - long: {}'.format(latitude, longitude))
            return False
