# ShipWell

A toy Django app that exposes and endpoint to get the current temperature from a given location.

## Using ShipWell
### Prerequisites

 Docker to build & run the repositories.

### Installation
To install from source, you have to clone the repository, and the use docker to build an image and run it.

```bash
git clone https://github.com/d-montenegro/ShipWell.git
cd ShipWell
make build run
```
This will start the application and keep it running on _localhost:8000_. You can stop it by hitting CTRL+C.

### Usage
This application exposes the single endpoint _average_temperature_, to consult the current temperature on a given location in celsius degrees. It retrieves the current temperature from multiple sources and serves the average.

It accepts the following parameters:
 * _zip_code_: this allows to refer to a location by a zip code
 * _latitude_: the latitude coordinate of a given location
 * _longitude_: the longitude coordinate of a given location
 * _filters_: the list of sources to consult current temperature from

**Note**: if _zip_code_ parameter is present, _latitude_ and _longitude_ are ignored. The allowed sources to filter by are: _noaa_, _accuweather_ and _weather.com_. If filters is not specified, then all of the sources are considered.

**Important**: This application uses [Google Maps API](https://developers.google.com/maps/documentation/geocoding/intro), to get longitude and latitude coordinates from a give zip code, and to validate input latitude and longitude coordinates as well. For this two work, an [API Key](https://developers.google.com/maps/documentation/geocoding/get-api-key) must be specified in project's settings files (ShipWell/ship_well/ship_well/settings.py), in the key GOOGLE_MAPS_API_KEY. However, this is not mandatory, as zip code parameter is not mandatory and coordinates validation is disabled by default. You can enable it by setting to _True_ the key ENABLE_COORDINATES_CHECKING in settings file. For any change in settings file to take place, the docker image must be re-generated. It can be done with the following code:
```bash¡
make build
```
### Example
To get the current temperature from latitude, longitude 40.714224,-73.961452, from AccuWeather, enter the following URL in your web browser:
 ```bash
 http://127.0.0.1:8000/average_temperature?latitude=40.7142240&longitude=-73.961452&filters=accuweather
```
Response:
```json
{"celsius": 12.0}
```
### Disclaimer
Currently, the unit test suite for this project is not fully implemented. Finishing it is prioritary and must be the following task.

### Optimization
This project can be optimized to perform the requests to external resources concurrently. This can be achieved with low effort using asyncio. This is specially important if the number a external sources to communicate with grows.
