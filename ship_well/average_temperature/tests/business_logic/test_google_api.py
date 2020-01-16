from average_temperature.business_logic.google_api.client import GoogleApiClient


# TODO: add tests cases for unexpected status_code / response


def test_location_from_zip_code_successfully_retrieved(requests_mock_get):
    """
    Check that location by a given zip_code is successfully retrieved using the google api
    """
    get, response = requests_mock_get
    response.status_code = 200
    response.json = lambda: {
        'status':  'OK',
        'results': [{
            'geometry': {
                'location': {
                    'lat': '123456.1', 'lng': '789.2'
                }
            }
        }]
    }

    api = GoogleApiClient(api_key='1234')
    lat, lng = api.get_location_from_zip_code(zip_code='ABCD')

    # check the coordinates are successfully retrieved
    assert lat == 123456.1
    assert lng == 789.2

    # check the request is made properly
    get.assert_called_with(GoogleApiClient.GOOGLE_MAPS_API_URL, params={'key': '1234',
                                                                        'components': 'postal_code:ABCD'})


def test_valid_coordinates_are_successfully_validated(requests_mock_get):
    """
    Check valid lat, long coordinates are successfully validated
    """
    get, response = requests_mock_get
    response.status_code = 200
    response.json = lambda: {
        'status':  'OK',
        'results': [{'foo': 'bar'}]
    }

    api = GoogleApiClient(api_key='1234')

    # check coordinates are successfully validated
    assert api.check_coordinates_validity(latitude=123456.1, longitude=789.2) is True

    # check the request is made properly
    get.assert_called_with(GoogleApiClient.GOOGLE_MAPS_API_URL, params={'key': '1234', 'latlng': '123456.1,789.2'})
