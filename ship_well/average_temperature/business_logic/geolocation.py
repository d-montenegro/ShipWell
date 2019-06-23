"""
This modules isolates the logic to interact with the internals to communicate with Google Maps API to
perform google_api and reverse google_api
"""
from typing import Tuple

from ship_well.settings import GOOGLE_MAPS_API_KEY
from .google_api.client import GoogleApiClient


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Check a given latitude - longitude coordinates belongs to an existing location

    :param latitude: the desired latitude
    :param longitude: the desired longitude
    :return: True if the coordinates are valid. False otherwise
    """
    geocode = GoogleApiClient(GOOGLE_MAPS_API_KEY)
    return geocode.validate_coordinates(latitude, longitude)


def get_coordinates_from_zip_code(zip_code: str) -> Tuple[float, float]:
    """
    Get the coordinates of a location given its zip_code

    :param zip_code: the desired zip_code
    :return: the tuple latitude - longitude
    :raises TemperatureAverageException if translation fails
    """
    geocode = GoogleApiClient(GOOGLE_MAPS_API_KEY)
    return geocode.get_location_from_zip_code(zip_code)
