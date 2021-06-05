# -*- coding: utf-8 -*-
"""

Reads the quality controlled 1-min weather data files of a complete year
(file nomenclature e.g. Meteo_1min_2021_qc.csv), collected by the current
Automatic Weather Station (CR1000 datalogger) of the LAPUP.

Version for the years > 2016.

The file contains (column index in file, first column index = 0):
    
    Time stamp: yyyy-mm-dd hh:mm:ss (0)
    Temperature 'T' (°C) (1)
    Relative humidity 'phi' (%) (2)
    Wind vector 'ws', 'wd' (m/s, °) (speed 3, direction 4)
    Wind gust vector 'wgust','wd' (m/s, °) (gust 5, direction 4)
    Precipitation 'precip' (mm) (6)
    Pressure 'pres' (hPa) (7)
    Logger battery voltage 'bat' (V) (8)

Header used in input file:

'time', 'T', 'phi', 'ws','wd', 'wgust', 'P', 'p', 'bat'

Quality control criteria have been set with the "Guidelines on Quality Control
Procedures for Data from Automatic Weather Stations" (WMO, 2014)

Ver. 1 LAPUP, A. Argiriou, 2021-06-05

"""

import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from windrose import WindroseAxes


def wind_direction(u, v):
    if u > 0.:
        phi0 = 180.
    else:
        phi0 = 0.
    wind_dir = 90. - 180 / np.pi * np.arctan(v / u) + phi0
    return np.round(wind_dir, 1)


start_time = time.time()

# Year to be processed

annum = '2021'

df = pd.read_csv('Meteo_1min_' + annum + '_qc.csv', index_col='Time', parse_dates=True, low_memory=False)


# Calculation of hourly averages

df_h = pd.DataFrame()  # definition of hourly dataframe

# Convert horizontal wind speed and direction to zonal and meridional component

df['wind_u'] = -df['ws'] * np.sin(df['wd'] * np.pi / 180.)
df['wind_v'] = -df['ws'] * np.cos(df['wd'] * np.pi / 180.)

# Calculation of hourly averages

for parameter in ['T', 'phi', 'pres', 'wind_u', 'wind_v']:
    df_h[parameter] = df[parameter].resample('h').mean()

df_h['ws'] = np.sqrt(df_h['wind_u'] ** 2 + df_h['wind_v'] ** 2)

wd_hourly = np.zeros(shape=(len(df_h['ws']), 1))

for i in range(len(df_h['wind_u'])):
    wd_hourly[i] = wind_direction(df_h['wind_u'][i], df_h['wind_v'][i])

df_h['wd'] = pd.DataFrame(wd_hourly, index=df_h.index)

# Calculation of hourly sums

df_h['precip'] = df['precip'].resample('h').sum()

df_h.to_csv('Meteo_hourly_' + annum + '_qc.csv', float_format='%.2f')

print('Elapsed time = {0:6.4f} s'.format(time.time()-start_time))
