"""
This module exposes a single function to get the current temperate as an average from several sources.
It abstracts all the internals.
"""
from typing import List
from statistics import mean

from .temperature_source import WEATHER_SOURCE

# This imports are needed to register weather sources
from .temperature_source import (  # noqa: F401
    accuweather,
    noaa,
    weatherdotcom,
)


def get_average_temperature(latitude: float, longitude: float, filter_: List[str] = None) -> float:
    """
    Retrieve current temperature as an average from several sources

    All the available sources are queried to retrieve the current temperature in
    celsius grades. Sources can be filtered, but note the following:
     - If no filter is provided, all the sources are queried.
     - If a value in the filter doesn't match an existing filter, it's ignored.

    :param latitude: the desired latitude
    :param longitude: the desired longitude
    :param filter_: source filters, by name
    :return: the average current temperature
    :raises WeatherAverageException if any source can't be requested
    :
    """
    if filter_:
        desired_sources = {source: func
                           for source, func in WEATHER_SOURCE.items()
                           if source in filter_}
    else:
        desired_sources = WEATHER_SOURCE

    all_weathers = [
        weather_func(latitude, longitude)
        for source, weather_func in desired_sources.items()
    ]

    return mean(all_weathers)


def get_valid_sources() -> List[str]:
    """
    Return all valid sources for requesting current temperature
    :return: a list of valid source names
    """
    return WEATHER_SOURCE.keys()

