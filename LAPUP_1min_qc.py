# -*- coding: utf-8 -*-
"""

Quality control checks on the raw 1-min weather data files of a complete year
(file nomenclature e.g. Meteo_1min_2017_raw.dat), collected by the current 
Automatic Weather Station (CR1000 datalogger) of the LAPUP.

Version for the years > 2016.

The file contains (column index in file, first column index = 0):
    
    Temperature 'T' (°C) (4)
    Relative humidity 'phi' (%) (5)
    Wind vector 'ws', 'wd' (m/s, °) (speed 6, direction 7)
    Wind gust vector 'wgust','wd' (m/s, °) (gust 8, direction 7)
    Precipitation 'P' (mm) (9)
    Pressure 'p' (hPa) (10)
    Logger battery voltage 'bat' (V) (11)

Header used:

'time', 'T', 'phi', 'ws','wd', 'wgust', 'P', 'p', 'bat'

Quality control criteria have been set with the "Guidelines on Quality Control
Procedures for Data from Automatic Weather Stations" (WMO, 2014)

Ver. 1 LAPUP, A. Argiriou, 2017-10-23
Ver. 2 LAPUP, A. Argiriou, 2020-01-29 (Correction of errors due to package upgrades)

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

header = ['time', 'T', 'phi', 'ws', 'wd', 'wg', 'precip', 'pres', 'bat']

df = pd.read_csv('Meteo_1min_' + annum + '_raw.dat', usecols=header, index_col='time', parse_dates=True,
                 low_memory=False)

# Dumps duplicate values

df = df[~df.index.duplicated(keep='first')]

# Creates 1-min time series

first = df.iloc[0].name
last = df.iloc[-1].name
dr = pd.date_range(first, last, freq='1min', name='Time')
df = df.reindex(dr)

# Extracts index of missing values

nans = df[df['T'].isnull()].index

# Opens log file and writes indexes of missing values

log_file = open('Meteo_' + annum + '_log.txt', 'w')
log_file.write('Year ' + annum + '\n')
log_file.write('Missing values\n')

for i in range(0, len(nans)):
    log_file.write(nans[i].strftime('%Y-%m-%d %H:%M:%S\n'))

log_file.write('{0:6d} missing values over a total of {1:6d}, or {2:4.2f} % \n'
               '\n'.format(len(nans), len(df), len(nans) * 100. / len(df)))

# Defines and checks the range of each parameter

temp = {'name': 'T', 'alias': 'Temperature', 'min': -2.0, 'max': 41.0}
rh = {'name': 'phi', 'alias': 'Relative humidity', 'min': 5.0, 'max': 100.0}
precip = {'name': 'precip', 'alias': 'Precipitation', 'min': 0.0, 'max': 40.0}
press = {'name': 'pres', 'alias': 'Pressure', 'min': 970.0, 'max': 1030.0}
batt = {'name': 'bat', 'alias': 'Battery voltage', 'min': 8.5, 'max': 15.0}
wspeed = {'name': 'ws', 'alias': 'Wind Speed', 'min': 0.0, 'max': 75.0}
wgust = {'name': 'wg', 'alias': 'Wind gust', 'min': 0.0, 'max': 75.0}
wdir = {'name': 'wd', 'alias': 'vane', 'min': 0.0, 'max': 360.0}

for parameter in [temp, rh, precip, press, batt, wspeed, wgust]:
    log_file.write('\n')
    log_file.write('Plausible out-of-range ' + parameter['alias'] + ' values\n')
    for i in range(0, len(df[parameter['name']])):
        if df[parameter['name']][i] < parameter['min']:
            log_file.write(str(df[parameter['name']][[i]]))
        if df[parameter['name']][i] > parameter['max']:
            log_file.write(str(df[parameter['name']][[i]]))

log_file.close()

# Plots the various parameters together with battery voltage

for parameter in [temp, rh, precip, press, batt, wspeed, wgust]:
    fig, ax1 = plt.subplots()
    ax1.plot(df[parameter['name']], color='b')
    ax1.set_xlabel('Date')

    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel(parameter['alias'], color='b')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    ax2.plot(df['bat'], color='r')
    ax2.set_ylabel('Battery voltage', color='r')
    ax2.tick_params('y', colors='r')

    fig.tight_layout()
    plt.savefig(parameter['name'] + '.pdf')
    plt.show()

# Replace outliers with NaN

for parameter in [temp, rh, precip, press, wspeed, wgust, wdir]:
    df.loc[df.bat < 9., parameter['name']] = np.NaN
    df.loc[df[parameter['name']] < parameter['min'], parameter['name']] = np.NaN
    df.loc[df[parameter['name']] > parameter['max'], parameter['name']] = np.NaN

df.to_csv('Meteo_1min_' + annum + '_qc.csv', float_format='%.1f')

# Plotting wind rose

# Necessary to plot pies instead of triangles
# see: https://github.com/python-windrose/windrose/issues/43
plt.hist([0, 1])
plt.close()

ax = WindroseAxes.from_ax()
ax.bar(df['wd'][df['ws'] > 0], df['ws'][df['ws'] > 0], normed=False,
       opening=0.8, edgecolor='black', bins=np.arange(0, 24, 4))
ax.legend(loc=2, title='Wind speed (m/s)')

plt.savefig('windrose' + annum + '.pdf')
plt.show()

# Averages after quality control

# Convert horizontal wind speed and direction to zonal and meridional values

df['wind_u'] = -df['ws'] * np.sin(df['wd'] * np.pi / 180.)
df['wind_v'] = -df['ws'] * np.cos(df['wd'] * np.pi / 180.)

log_file = open('Meteo_' + annum + '_log.txt', 'a+')
log_file.write('\n')

for parameter in ['T', 'phi', 'pres']:
    log_file.write(parameter + ' averages\n')
    log_file.write(str(df[parameter].resample('M').mean()))
    log_file.write('\n')
    log_file.write(str(df[parameter].resample('Y').mean()))
    log_file.write('\n')

log_file.write('\n')
log_file.write('Wind speed and direction' + ' averages\n')
log_file.write('Monthly averages\n')

wind_u_monthly = df['wind_u'].resample('M').mean()
wind_v_monthly = df['wind_v'].resample('M').mean()
ws_monthly = np.sqrt(wind_u_monthly ** 2 + wind_v_monthly ** 2)

wd_monthly = np.zeros(shape=(12, 1))
for i in range(0, len(wind_u_monthly)):
    wd_monthly[i] = wind_direction(wind_u_monthly[i], wind_v_monthly[i])
wd_monthly = pd.DataFrame(wd_monthly, index=ws_monthly.index)

log_file.write(str(ws_monthly))
log_file.write('\n')
log_file.write(str(wd_monthly))
log_file.write('\n')

log_file.write('Annual averages\n')
wind_u_annual = df['wind_u'].resample('Y').mean()
wind_v_annual = df['wind_v'].resample('Y').mean()
ws_annual = np.sqrt(wind_u_annual ** 2 + wind_v_annual ** 2)
wd_annual = wind_direction(wind_u_annual.values, wind_v_annual.values)
log_file.write(str(ws_annual))
log_file.write('\n')
log_file.write(str(wd_annual))
log_file.write('\n')

log_file.write('Precipitation' + ' sums\n')
log_file.write(str(df['precip'].resample('M').sum()))
log_file.write(str(df['precip'].resample('Y').sum()))

limit = [3, 10, 20]
i_limit = 0
for parameter in ['T', 'phi', 'ws']:
    log_file.write(parameter)
    df1 = df[parameter].dropna()
    log_file.write(str(df1[np.gradient(df1) >= limit[i_limit]]))
    i_limit = i_limit + 1

log_file.close()

print('Elapsed time = {0:6.4f} s'.format(time.time()-start_time))
