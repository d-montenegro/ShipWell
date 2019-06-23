from django.http import JsonResponse
from .business_logic import (
    get_average_temperature,
    get_valid_sources,
    get_coordinates_from_zip_code,
    validate_coordinates
)

from .business_logic.exceptions import TemperatureAverageException



def average_temperature(request):
    """

    :param request:
    :return:
    """
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    zip_code = request.GET.get('zip_code')

    if zip_code:
        print(get_coordinates_from_zip_code(zip_code))

    if not latitude or not longitude:
        return JsonResponse({'error': 'latitude and/or longitud params are missing'}, status=400)

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return JsonResponse({'error': 'latitude and longitude must be numeric values'}, status=400)
    filters = request.GET.getlist('filters')
    print(filters)
    if filters:
        missing_sources = set(filters) - set(get_valid_sources())
        if missing_sources:
            return JsonResponse(
                {'error': 'The following filters provided are invalid: {}'.format(missing_sources)},
                status=400
            )

    try:
        average_weather = get_average_temperature(latitude, longitude, filters)
    except TemperatureAverageException:
        return JsonResponse(
            {'error': 'Could not fetch current temperature'},
            status=500
        )
    else:
        return JsonResponse({'celsius': average_weather})
