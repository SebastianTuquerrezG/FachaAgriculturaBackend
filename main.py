"""
This module is the main entry point for the application. It defines the FastAPI
application and the endpoints for querying weather data and geolocating the user.
"""

import datetime
import uvicorn
from fastapi import FastAPI
from app.meteomatics_api import MeteomaticsAPI
from app.google_api import GoogleAPI


app = FastAPI()
meteomatics_api = MeteomaticsAPI()
google_api = GoogleAPI()


@app.get("/")
def read_root() -> dict:
    """
    Returns a list of available endpoints for the application.
    """

    return {
        "endpoints": [
            "/",
            "/weather_data",
            "/geolocate"
        ]
    }


@app.post("/weather_data")
def weather_data(body: dict) -> dict:
    """
    Queries the Meteomatics API for weather data based on the given parameters.
    """

    data = meteomatics_api.query_grid_timeseries(
        datetime.datetime.strptime(
            body['start_date'], "%Y-%m-%d").timetuple()[:3],
        body['interval_hours'],
        body['end_interval_days'],
        body['north_latitude'],
        body['west_longitude'],
        body['south_latitude'],
        body['east_longitude'],
        body['latitude_resolution'],
        body['longitude_resolution']
    )

    return data


@app.post("/heat_data")
def heat_data(body: dict):
    """
    Queries the Meteomatics API for heat data based on the given parameters.
    """
    data = meteomatics_api.query_heat_timeseries(
        datetime.datetime.strptime(
            body['start_date'], "%Y-%m-%d").timetuple()[:3],
        body['interval_hours'],
        body['end_interval_days'],
        body['north_latitude'],
        body['west_longitude'],
        body['south_latitude'],
        body['east_longitude'],
        body['latitude_resolution'],
        body['longitude_resolution']
    )

    return data


@app.get("/geolocate")
def geolocate() -> dict:
    """
    Geolocates the user's IP address using the Google Maps Geolocation API.
    """

    return google_api.geolocate()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
