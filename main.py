from fastapi import FastAPI
from app.meteomatics_api import MeteomaticsAPI

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
