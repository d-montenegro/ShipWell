"""
This module exposes a single function to get the current temperate as an average from several sources.
It abstracts all the internals.
"""
from concurrent import futures
from typing import List
from statistics import mean

from .temperature_source.sources import WebAppTemperatureSource, WEATHER_SOURCE


MAX_CONCURRENT_WORKERS = 3


def get_average_temperature(latitude: float, longitude: float, filter_: List[str] = None) -> float:
    """
    Retrieve current temperature as an average from several sources

    All the available sources are queried to retrieve the current temperature in
    celsius degrees. Sources can be filtered, but note the following:
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

    workers = min(MAX_CONCURRENT_WORKERS, len(desired_sources))
    with futures.ThreadPoolExecutor(workers) as executor:
        all_weathers = executor.map(
            lambda source: WebAppTemperatureSource.from_source_name(source).get_current_temperature(latitude,
                                                                                                    longitude),
            desired_sources.keys()
        )

    return mean(all_weathers)


def get_valid_sources() -> List[str]:
    """
    Return all valid sources for requesting current temperature
    :return: a list of valid source names
    """
    return WEATHER_SOURCE.keys()
