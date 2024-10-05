from __future__ import print_function
import pandas as pd
from dotenv import load_dotenv
import os

# 1. Importa los módulos necesarios: datetime y meteomatics.api.
import datetime as dt
import meteomatics.api as api

load_dotenv()
pd.set_option('display.max_rows', 100)

# 2. Define las credenciales de autenticación: nombre de usuario y contraseña.
username = os.getenv('USERNAMEAPI')
password = os.getenv('PASSWORD')

# 3. Obtiene la fecha y hora actual en formato UTC y la establece a medianoche.
now = dt.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

# 4. Calcula la fecha de inicio y fin de la consulta sumando y restando un día a partir de la fecha actual.
print(now)
startdate_ts = now
enddate_ts = startdate_ts + dt.timedelta(days=10)

# 5. Establece el intervalo de tiempo para la consulta en una hora.
interval_ts = dt.timedelta(hours=12)

# 6. Define los parámetros de la serie de tiempo que se desea obtener: temperatura a 2 metros y precipitación en una hora.
parameters_ts = ['t_2m:C', 'precip_1h:mm']

# 7. Define las coordenadas geográficas del área de consulta: latitud N, longitud O, latitud S y longitud E.
# Define las coordenadas geográficas del área de consulta para el Cauca Colombia:
lat_N = 3.5
lon_W = -78.5
lat_S = 1.5
lon_E = -75.5


# 8. Define la resolución de la grilla en latitud y longitud.
res_lat = 0.5
res_lon = 0.5

# 9. Realiza la consulta a la API utilizando la función query_grid_timeseries y los parámetros definidos.
print("grid timeseries:")
try:
    df_grid_timeseries = api.query_grid_timeseries(startdate_ts, enddate_ts, interval_ts, parameters_ts, lat_N,
                                                   lon_W, lat_S, lon_E, res_lat, res_lon, username, password)
    # 10. Imprime las primeras filas de la serie de tiempo obtenida.
    print(df_grid_timeseries)

    df_grid_timeseries.to_csv(
        'dataset.csv')


except Exception as e:
    # Captura y muestra un mensaje de error si ocurre alguna excepción durante la consulta a la API.
    print("Failed, the exception is {}".format(e))

# 11. Calcula la temperatura máxima, mínima y media de la serie de tiempo.
maximum_temperature = df_grid_timeseries['t_2m:C'].max()
minimum_temperature = df_grid_timeseries['t_2m:C'].min()
mean_temperature = df_grid_timeseries['t_2m:C'].mean()

# 12. Obtiene la columna de precipitación en una hora.
just_precipitation = df_grid_timeseries['precip_1h:mm']

# 13. Obtiene el primer valor de precipitación en una hora.
first_value_of_precipitation = df_grid_timeseries.iloc[0]['precip_1h:mm']

# 14. Filtra la serie de tiempo para obtener solo los datos correspondientes a las 12 UTC.
just_at_12UTC = df_grid_timeseries[df_grid_timeseries.index.get_level_values(
    'validdate').hour == 12]
