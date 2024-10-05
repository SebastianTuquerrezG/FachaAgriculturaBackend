from fastapi import FastAPI
from app.meteomatics_api import MeteomaticsAPI
import requests
import googlemaps
import os

app = FastAPI()
meteomatics_api = MeteomaticsAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/weather_data")
def read_item():
    df_grid_timeseries = meteomatics_api.query_grid_timeseries()
    print(df_grid_timeseries)

    return {
        "df_grid_timeseries": df_grid_timeseries.to_dict(orient="records")
    }

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