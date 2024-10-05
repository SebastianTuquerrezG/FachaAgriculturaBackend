from fastapi import FastAPI
from app.meteomatics_api import MeteomaticsAPI
import requests
import googlemaps
import os
import datetime

app = FastAPI()
meteomatics_api = MeteomaticsAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/weather_data")
def weather_data(body: dict):
    startdate_ts = body['startdate_ts']
    hours = body['hours']
    days = body['days']
    lat_n = body['lat_n']
    lon_w = body['lon_w']
    lat_s = body['lat_s']
    lon_e = body['lon_e']
    res_lat = body['res_lat']
    res_lon = body['res_lon']

    date_obj = datetime.datetime.strptime(startdate_ts, "%Y-%m-%d")
    date_tuple = (date_obj.year, date_obj.month, date_obj.day)

    data = meteomatics_api.query_grid_timeseries(
        date_tuple, hours, days, lat_n, lon_w, lat_s, lon_e, res_lat, res_lon)

    return data


key = os.getenv('GOOGLE_API_KEY')
url = f'https://www.googleapis.com/geolocation/v1/geolocate?key={key}'


@app.post("/geolocate/")
def geolocate():
    # Datos del cuerpo de la solicitud
    data = {
        "considerIp": "true"
    }

    # Petición POST
    response = requests.post(url, json=data)

    if response.status_code == 200:
        respuesta = response.json()

        latitud = respuesta.get('location', {}).get('lat')
        longitud = respuesta.get('location', {}).get('lng')

        return {
            "latitud": latitud,
            "longitud": longitud
        }
    else:
        return {"error": response.status_code, "message": response.text}
