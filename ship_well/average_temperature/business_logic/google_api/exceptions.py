"""
This modules holds all the exception raised by google_api package
"""
from ..exceptions import (
    TemperatureAverageException,
    ServiceUnexpectedResponse,
    ServiceConnectionError,
    ServiceUnexpectedStatusCode
)


class GoogleAPIException(TemperatureAverageException):
    """
    Base exception for GeoCode logic
    """
    pass


class GoogleAPIConnectionError(GoogleAPIException, ServiceConnectionError):
    """
    This exception is raised when the geo code service is not available
    """
    pass


class GoogleAPIUnexpectedResponse(GoogleAPIException, ServiceUnexpectedResponse):
    """
    This exception is raised when the response from the geo code service is not as expected
    """
    pass


class GoogleAPIUnexpectedStatusCode(GoogleAPIException, ServiceUnexpectedStatusCode):
    """
    This exception is raised when the HTTP ERROR code from the response is unexpected
    """

    def __init__(self, response):
        super().__init__(response, 'Unexpected status code')
