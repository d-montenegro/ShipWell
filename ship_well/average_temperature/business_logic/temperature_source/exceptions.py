"""
This module defines all the exceptions that are being raised by this package
"""

from ..exceptions import (
    TemperatureAverageException,
    ServiceUnexpectedResponse,
    ServiceConnectionError,
    ServiceUnexpectedStatusCode,
)


class TemperatureSourceException(TemperatureAverageException):
    """
    This is the base exception class for all weather source package
    """
    pass


class TemperatureSourceConnectionError(TemperatureSourceException, ServiceConnectionError):
    """
    This exception is raised when there are connection issues
    """
    pass


class TemperatureSourceUnexpectedResponse(TemperatureSourceException, ServiceUnexpectedResponse):
    """
    This exception is raised when the response can not be parsed successfully
    """
    pass


class TemperatureSourceUnexpectedStatusCode(TemperatureSourceException, ServiceUnexpectedStatusCode):
    """
    This exception is raised when the response HTTP_ERROR_CODE is unexpected
    """
    pass
