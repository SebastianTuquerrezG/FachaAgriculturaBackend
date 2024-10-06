"""
A module that interacts with the Meteomatics API to query weather data.
"""

import os
import datetime as dt
from dotenv import load_dotenv
import meteomatics.api as api
import pandas as pd


load_dotenv()


class MeteomaticsAPI:
    """
    A class that interacts with the Meteomatics API to query weather data.

    Attributes:
        username (str): The username for accessing the Meteomatics API.
        password (str): The password for accessing the Meteomatics API.

    Methods:
        data_to_json(data) -> dict:
            Converts the given data to a dictionary format.

        query_grid_timeseries(start_date, interval_hours, end_interval_days,
                              north_latitude, west_longitude, south_latitude, east_longitude,
                              latitude_resolution, longitude_resolution) -> dict:
            Queries the grid timeseries data from the Meteomatics API.

        get_temperature_stats(df_grid_timeseries) -> dict:
            Calculates the maximum, minimum, and mean temperature from the given
            grid timeseries data.
    """

    def __init__(self):
        self.username = os.getenv('USERNAMEAPI')
        self.password = os.getenv('PASSWORD')

    def data_to_json(self, data) -> dict:
        """
        Converts the given data to a dictionary format.

        Args:
            data: The data to be converted.

        Returns:
            A dictionary representation of the data.
        """

        df = pd.DataFrame(data)
        df_reset = df.reset_index()
        df_reset = df.reset_index().copy()
        df_reset['validdate'] = df_reset['validdate'].astype(str)

        dict_data = df_reset.to_dict(orient='records')
        return dict_data

    def query_grid_timeseries(self,
                              start_date,
                              interval_hours: int,
                              end_interval_days: int,
                              north_latitude: float,
                              west_longitude: float,
                              south_latitude: float,
                              east_longitude: float,
                              latitude_resolution: float,
                              longitude_resolution: float) -> dict:
        """
        Queries the grid timeseries data from the Meteomatics API.

        Args:
            start_date: The start date of the query.
            interval_hours (int): The interval in hours between data points.
            end_interval_days (int): The number of days to query.
            north_latitude (float): The latitude of the northern boundary.
            west_longitude (float): The longitude of the western boundary.
            south_latitude (float): The latitude of the southern boundary.
            east_longitude (float): The longitude of the eastern boundary.
            latitude_resolution (float): The resolution of the latitude grid.
            longitude_resolution (float): The resolution of the longitude grid.

        Returns:
            A dictionary containing the queried grid timeseries data and temperature statistics.
        """

        try:
            start_date = dt.datetime(*start_date)
            df_grid_timeseries = api.query_grid_timeseries(
                startdate=start_date,
                enddate=start_date + dt.timedelta(days=end_interval_days),
                lat_N=north_latitude,
                lon_W=west_longitude,
                lat_S=south_latitude,
                lon_E=east_longitude,
                interval=dt.timedelta(hours=interval_hours),
                parameters=['t_2m:C', 'precip_1h:mm'],
                res_lat=latitude_resolution,
                res_lon=longitude_resolution,
                username=self.username,
                password=self.password
            )

            grid_timeseries_data = self.data_to_json(df_grid_timeseries)
            get_temperature_stats_data = self.get_temperature_stats(
                df_grid_timeseries)

            data = {
                "temperature_stats": get_temperature_stats_data,
                "grid_timeseries": grid_timeseries_data
            }
            return data

        except Exception as e:
            return {"error": str(e)}

    def query_heat_timeseries(self,
                              start_date,
                              interval_hours: int,
                              end_interval_days: int,
                              north_latitude: float,
                              west_longitude: float,
                              south_latitude: float,
                              east_longitude: float,
                              latitude_resolution: float,
                              longitude_resolution: float) -> dict:
        try:
            start_date = dt.datetime(*start_date)

            df_heat_timeseries = api.query_grid_timeseries(
                startdate=start_date,
                enddate=start_date + dt.timedelta(days=end_interval_days),
                lat_N=north_latitude,
                lon_W=west_longitude,
                lat_S=south_latitude,
                lon_E=east_longitude,
                interval=dt.timedelta(hours=interval_hours),
                parameters=['t_2m:C', 'precip_1h:mm'],
                res_lat=latitude_resolution,
                res_lon=longitude_resolution,
                username=self.username,
                password=self.password
            )

            print(f"Response of API: {df_heat_timeseries}")

            df_heat_timeseries.reset_index(inplace=True)
            df_heat_timeseries['validdate'] = pd.to_datetime(
                df_heat_timeseries['validdate'])

            daily_max_temps = df_heat_timeseries.groupby(
                df_heat_timeseries['validdate'].dt.date)['t_2m:C'].max()
            daily_min_temps = df_heat_timeseries.groupby(
                df_heat_timeseries['validdate'].dt.date)['t_2m:C'].min()

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
                    break

            return {
                "data": self.data_to_json(df_heat_timeseries),
                "daily_max_temperatures": daily_max_temps.to_dict(),
                "daily_min_temperatures": daily_min_temps.to_dict(),
                "potential_heat_wave": heat_days if consecutive_heat_days >= consecutive_days_threshold else []
            }
        except Exception as e:
            print(f"Error to request the heat wave indicator: {e}")
            return {"error": "Error to get the hear wave indicator"}, 500

    def get_temperature_stats(self, df_grid_timeseries) -> dict:
        """
        Calculates the maximum, minimum, and mean temperature from the given grid timeseries data.

        Args:
            df_grid_timeseries: The grid timeseries data.

        Returns:
            A dictionary containing the maximum, minimum, and mean temperature.
        """

        maximum_temperature = df_grid_timeseries['t_2m:C'].max()
        minimum_temperature = df_grid_timeseries['t_2m:C'].min()
        mean_temperature = df_grid_timeseries['t_2m:C'].mean()

        data = {
            "maximum_temperature": float(maximum_temperature),
            "minimum_temperature": float(minimum_temperature),
            "mean_temperature": float(mean_temperature)
        }
        return data
