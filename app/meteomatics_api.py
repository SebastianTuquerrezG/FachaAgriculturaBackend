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
            
    def query_heat_timeseries(self, startdate_ts, hours: int, days: int, lat_n: float, lon_w: float, lat_s: float, lon_e: float, res_lat: float, res_lon: float):
        try:
            startdate_ts = dt.datetime(*startdate_ts)
            
            df_heat_timeseries = api.query_grid_timeseries(
                startdate=startdate_ts,
                enddate=startdate_ts + dt.timedelta(days=days),
                lat_N=lat_n,
                lon_W=lon_w,
                lat_S=lat_s,
                lon_E=lon_e,
                interval=dt.timedelta(hours=hours),
                parameters=['t_2m:C'],  
                res_lat=res_lat,
                res_lon=res_lon,
                username=self.username,
                password=self.password
            )
            
            print(f"Respuesta de la API: {df_heat_timeseries}")
            
            df_heat_timeseries.reset_index(inplace=True)
            df_heat_timeseries['validdate'] = pd.to_datetime(df_heat_timeseries['validdate'])
            
            daily_max_temps = df_heat_timeseries.groupby(df_heat_timeseries['validdate'].dt.date)['t_2m:C'].max()
            daily_min_temps = df_heat_timeseries.groupby(df_heat_timeseries['validdate'].dt.date)['t_2m:C'].min()
            
            max_temp_threshold = 35  # °C
            min_temp_threshold = 20   # °C
            consecutive_days_threshold = 3
            
            consecutive_heat_days = 0
            heat_days = []
            
            for date in daily_max_temps.index:
                max_temp = daily_max_temps[date]
                min_temp = daily_min_temps[date]
                
                if max_temp > max_temp_threshold and min_temp > min_temp_threshold:
                    consecutive_heat_days += 1
                    heat_days.append(date)
                else:
                    consecutive_heat_days = 0            

                if consecutive_heat_days >= consecutive_days_threshold:
                    print(f"Ola de calor detectada a partir del {heat_days[0]} durante {consecutive_heat_days} días.")
                    break 

            return {
                "data": self.data_to_json(df_heat_timeseries),
                "daily_max_temperatures": daily_max_temps.to_dict(),
                "daily_min_temperatures": daily_min_temps.to_dict(),
                "potential_heat_wave": heat_days if consecutive_heat_days >= consecutive_days_threshold else []
            }
        except Exception as e:
            print(f"Error al consultar la serie temporal de índice de calor: {e}")
            return {"error": "Error al obtener los datos de índice de calor"}, 500


    
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
