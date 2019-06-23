"""
This module contains all the exceptions thar being raised by all the business logic.
"""


class TemperatureAverageException(Exception):
    """
    Base exception for all the business logic exceptions
    """
    pass


class ServiceConnectionError(TemperatureAverageException):
    pass


class ServiceUnexpectedResponse(TemperatureAverageException):
    def __init__(self, response, error_description):
        self.response = response
        self.error_description = error_description

    def __str__(self):
        return '{s.error_description}. Response: {s.response}'.format(s=self)


class ServiceUnexpectedStatusCode(ServiceUnexpectedResponse):
    def __init__(self, response):
        super().__init__(response, 'Unexpected status code')
