from django.http import JsonResponse
from .business_logic import get_average_temperature


def average_temperature(request):
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')

    filters = request.GET.get('filters')

    #TODO: exception handling
    average_weather = get_average_temperature(latitude, longitude, filters)

    return JsonResponse({'celcius': average_weather})
