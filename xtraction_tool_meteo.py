"""
Extracts specific weather parameters for specific time periods from the annual 1-min quality controlled files of the
LAPUP weather station.

Version for the years > 2016.

Input file: Meteo_1min_yyyy_qc.csv, yyyy: year to be processed, e.g. 2020

The file contains (column index in file, first column index = 0):

    Timestamp 'Time' (yyyy-mm-dd hh:MM:ss) (0)
    Temperature 'T' (°C) (1)
    Relative humidity 'phi' (%) (2)
    Wind vector 'ws', 'wd' (m/s, °) (speed 3, direction 4)
    Wind gust 'wg', (m/s) (5)
    Precipitation 'precip' (mm) (6)
    Pressure 'pres' (hPa) (7)
    Logger battery voltage 'bat' (V) (8)

Ver. 1 LAPUP, A. Argiriou, 2017-10-23
Ver. 2 LAPUP, A. Argiriou, 2020-02-07 (extracts specific parameters for a defined time)

"""

import pandas as pd
from datetime import datetime

# Input parameters

annum = '2020'  # Year to be processed

start_datetime = '2020-08-01 00:00:00'
end_datetime = '2020-09-30 23:59:00'


parameters = [0, 1, 2, 3, 4]  # parameters to be extracted; first index must be 0 to include timestamp.

df = pd.read_csv('Meteo_1min_' + annum + '_qc.csv', sep=',', usecols=parameters, index_col=0, parse_dates=True)

df.loc[start_datetime:end_datetime].to_csv('Meteo_1min_' + annum + '_range.csv')
