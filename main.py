from fastapi import FastAPI
from app.meteomatics_api import MeteomaticsAPI
import googlemaps

app = FastAPI()
meteomatics_api = MeteomaticsAPI()
gmaps = googlemaps.Client(key='AIzaSyB-e2EAWcPz5DFaT00Xu34SyTCPKSgsDek')


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

@app.post("/geocode/")
def get_coordinates(address: str):
    # Realizar la geocodificación
    geocode_result = gmaps.geocode(address)

    if geocode_result:
        # Extraer las coordenadas (latitud y longitud)
        coordenadas = geocode_result[0]['geometry']['location']
        return {
            "latitud": coordenadas['lat'],
            "longitud": coordenadas['lng']
        }
    else:
        return {"error": "No se encontraron coordenadas para la dirección proporcionada."}
