from fastapi import FastAPI
from app.meteomatics_api import WeatherData
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/weather_data")
def read_item():
    return WeatherData('restrepo_pablo', 'ou3J1Kx3KS').query_weather_data('2021-01-01T00:00:00Z', '2021-01-01T01:00:00Z', '1h', 't_2m:C,precip_1h:mm', 47.5, 8.5, 47.0, 9.0, 0.01, 0.01)
