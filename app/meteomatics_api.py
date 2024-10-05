import os
from dotenv import load_dotenv
import datetime as dt
import meteomatics.api as api
import pandas as pd
import json


load_dotenv()


class MeteomaticsAPI:
    def __init__(self):
        self.username = os.getenv('USERNAMEAPI')
        self.password = os.getenv('PASSWORD')

    def data_to_json(self, data):
        # Crear DataFrame a partir de los datos
        df = pd.DataFrame(data)

        # Restablecer los índices para que 'lat', 'lon', y 'validdate' se conviertan en columnas
        df_reset = df.reset_index()

        # Convertir la columna 'validdate' a string para evitar problemas de serialización
        df_reset['validdate'] = df_reset['validdate'].astype(str)

        # Convertir el DataFrame a diccionario orientado a registros
        dict_data = df_reset.to_dict(orient='records')

        # Convertir el diccionario a formato JSON
        json_data = json.dumps(dict_data, ensure_ascii=False)

        return json_data

    def query_grid_timeseries(self, startdate_ts, hours: int, days: int, lat_n: float, lon_w: float, lat_s: float, lon_e: float, res_lat: float, res_lon: float):
        try:
            startdate_ts = dt.datetime(*startdate_ts)
            df_grid_timeseries = api.query_grid_timeseries(
                startdate=startdate_ts,
                enddate=startdate_ts + dt.timedelta(days=days),
                lat_N=lat_n,
                lon_W=lon_w,
                lat_S=lat_s,
                lon_E=lon_e,
                interval=dt.timedelta(hours=hours),
                parameters=['t_2m:C', 'precip_1h:mm'],
                res_lat=res_lat,
                res_lon=res_lon,
                username=self.username,
                password=self.password
            )
            return self.data_to_json(df_grid_timeseries)
        except Exception as e:
            print(e)

    def get_temperature_stats(self, df_grid_timeseries):
        maximum_temperature = df_grid_timeseries['t_2m:C'].max()
        minimum_temperature = df_grid_timeseries['t_2m:C'].min()
        mean_temperature = df_grid_timeseries['t_2m:C'].mean()
        return maximum_temperature, minimum_temperature, mean_temperature

    def get_precipitation_data(self, df_grid_timeseries):
        just_precipitation = df_grid_timeseries['precip_1h:mm']
        first_value_of_precipitation = df_grid_timeseries.iloc[0]['precip_1h:mm']
        just_at_12UTC = df_grid_timeseries[df_grid_timeseries.index.get_level_values(
            'validdate').hour == 12]
        return just_precipitation, first_value_of_precipitation, just_at_12UTC
