"""
This module defines all the exceptions that are being raised by this package
"""

from ..exceptions import WeatherAverageException


class WeatherSourceException(WeatherAverageException):
    """
    This is the base exception class for all weather source package
    """
    pass


class AccuweatherInvalidRequest(WeatherSourceException):
    """
    This exception is raised when accuweather response's status code is different than success
    """
    pass


class AccuweatherUnexpectedResponse(WeatherAverageException):
    """
    This exception is raised when accuweather response's status code is success, but the json content is unexpected
    and can't be parsed successfully.
    """
    pass


class NoaaInvalidRequest(WeatherSourceException):
    """
    This exception is raised when noaa response's status code is different than success
    """
    pass


class WeatherDotComInvalidRequest(WeatherSourceException):
    """
    This exception is raised when weather.com response's status code is different than success
    """
    pass


class WeatherDotComUnexpectedResponse(WeatherSourceException):
    pass
