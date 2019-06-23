"""
This module isolates all the logic to retrieve current weather from external sources.

The logic to retrieve current weather from an arbitrary resource must be codified into a function
that receives as parameter a latitude and a longitude and returns the current temperature in celsius grades. That
function must be decorated with *register_weather_source* to register it and being available to use.
"""

import logging
from functools import wraps


logger = logging.getLogger(__name__)


WEATHER_SOURCE = {}


def register_weather_source(source_name: str):
    """
    This function registers a function to retrieve the current weather from an arbitrary source. That function
    must accept to floats as parameter, the latitude and the longitude of a given zone, and must return a float
    indicating the current temperature in celsius unit.

    :param source_name: and identifier for the querying source
    :return a decorator
    """
    def decorator(func):
        @wraps(func)
        def wrapper(latitude, longitude):
            return func(latitude, longitude)

        if source_name in WEATHER_SOURCE:
            logger.warning('Already registered a weather source with name %s. Skipping', source_name)
        else:
            WEATHER_SOURCE[source_name] = wrapper
        return wrapper
    return decorator
