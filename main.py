import os
import datetime
import requests
import uvicorn
from fastapi import FastAPI
from app.meteomatics_api import MeteomaticsAPI


app = FastAPI()
meteomatics_api = MeteomaticsAPI()

key = os.getenv('GOOGLE_API_KEY')
url = f'https://www.googleapis.com/geolocation/v1/geolocate?key={key}'


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


@app.get("/geolocate/")
def geolocate():
    data = {
        "considerIp": "true"
    }

    response = requests.post(url, json=data, timeout=10)

    if response.status_code == 200:
        response_data = response.json()
        print(response_data)

        latitude = response_data.get('location', {}).get('lat')
        longitude = response_data.get('location', {}).get('lng')

        return {
            "latitude": latitude,
            "longitude": longitude
        }
    return {"error": response.status_code, "message": response.text}


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
