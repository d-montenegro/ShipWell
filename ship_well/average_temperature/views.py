from typing import List

from django.http import JsonResponse
from .business_logic import (
    get_average_temperature,
    get_valid_sources,
    get_coordinates_from_zip_code,
    validate_coordinates,
    TemperatureAverageException,
    ServiceConnectionError,
    ServiceUnexpectedResponse,

)


def _handle_average_temperature_by_coordinates(
        latitude: float, longitude: float, filters: List[str] = None, validate: bool = True):
    """
    Builds a response with the average temperature for a given location

    Since coordinate validation depends on an external source, availability can't be guaranteed, so the validate
    flag can be used to disable it.

    :param latitude: the desired latitude
    :param longitude: the desired longitude
    :param filters: an optional list of the sources to consider
    :param validate: weather validate or the coordinates
    :return: the corresponding response
    """
    if validate:
        try:
            are_valid = validate_coordinates(latitude, longitude)
        except ServiceConnectionError:
            return JsonResponse(
                {'error': 'Can not connect to the underlying services to validate the coordinates'},
                status=500
            )
        except ServiceUnexpectedResponse:
            return JsonResponse(
                {'error': 'Could not validate the coordinates ({}, {})'.format(latitude, longitude)},
                status=500
            )
        else:
            if not are_valid:
                return JsonResponse(
                    {'error': 'The specified coordinates are invalid ({}, {})'.format(latitude, longitude)},
                    status=400
                )

    try:
        average_weather = get_average_temperature(latitude, longitude, filters)
        return JsonResponse({'celsius': average_weather})
    except TemperatureAverageException:
        return JsonResponse(
            {'error': 'Could not retrieve current temperature for location ({}, {})'.format(latitude, longitude)},
            status=500
        )


def _handle_average_temperature_by_zip_code(zip_code: str, filters: List[str] = None):
    """
    Builds a response with the average temperature for a given location

    :param zip_code: the desired zip_code
    :param filters: an optional list of the sources to consider
    :return: the corresponding response
    """
    try:
        coords = get_coordinates_from_zip_code(zip_code)
    except ServiceConnectionError:
        return JsonResponse(
            {'error': 'Can not connect to the underlying services to translate the zip code into coordinates'},
            status=500
        )
    except ServiceUnexpectedResponse:
        return JsonResponse(
            {'error': 'Could not get the location for zip_code {}'.format(zip_code)},
            status=500
        )
    else:
        if coords is None:
            return JsonResponse(
                {'error': 'The specified zip_code is invalid: {}'.format(zip_code)},
                status=400
            )
        latitude, longitude = coords
        return _handle_average_temperature_by_coordinates(latitude, longitude, filters, validate=False)


def average_temperature(request):
    """
    Retrieve the current temperature at a given location as an average of several sources.

    The query params accepted are the following:
     * zip_code: the zip_code of the desired location
     * latitude: the latitude coordinate of the desired location
     * longitude: the longitude coordinate of the desired location
     * filters: the list of sources to consider. The allowed are:
       - noaa
       - accuweather
       - weather.com

    *Note*: - if zip_code param is present, latitude and longitude params are ignored.
            - if filters param is not present, all the sources are considered
    """
    # check filters are valid
    filters = request.GET.getlist('filters')
    if filters:
        missing_sources = set(filters) - set(get_valid_sources())
        if missing_sources:
            return JsonResponse(
                {'error': 'The following provided filters are no valid: {}'.format(missing_sources)},
                status=400
            )

    zip_code = request.GET.get('zip_code')
    if zip_code:
        return _handle_average_temperature_by_zip_code(zip_code, filters)
    else:
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')

        if not latitude or not longitude:
            return JsonResponse({'error': 'latitude and/or longitud params are missing and zip_code is missing also'},
                                status=400)

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return JsonResponse({'error': 'latitude and longitude must be numeric values'}, status=400)
        else:
            return _handle_average_temperature_by_coordinates(latitude, longitude, filters, True)
