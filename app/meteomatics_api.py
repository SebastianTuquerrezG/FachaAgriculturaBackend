import pandas as pd
import os
from dotenv import load_dotenv
import datetime as dt
import meteomatics.api as api

load_dotenv()
pd.set_option('display.max_rows', 100)


class MeteomaticsAPI:
    def __init__(self):
        self.username = os.getenv('USERNAMEAPI')
        self.password = os.getenv('PASSWORD')
        self.now = dt.datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0)
        self.startdate_ts = self.now
        self.enddate_ts = self.startdate_ts + dt.timedelta(days=10)
        self.interval_ts = dt.timedelta(hours=12)
        self.parameters_ts = ['t_2m:C', 'precip_1h:mm']
        self.lat_N = 3.5
        self.lon_W = -78.5
        self.lat_S = 1.5
        self.lon_E = -75.5
        self.res_lat = 0.5
        self.res_lon = 0.5

    def query_grid_timeseries(self):
        try:
            df_grid_timeseries = api.query_grid_timeseries(
                self.startdate_ts,
                self.enddate_ts,
                self.interval_ts,
                self.parameters_ts,
                self.lat_N,
                self.lon_W,
                self.lat_S,
                self.lon_E,
                self.res_lat,
                self.res_lon,
                self.username,
                self.password
            )
            return df_grid_timeseries
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


print(MeteomaticsAPI().query_grid_timeseries())
