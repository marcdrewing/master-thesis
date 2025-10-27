import pandas as pd
import os
from datetime import datetime
import shutil
import time

filename_meausurementData   = "Test"#ends with .csv

####################### clean csv file with recorded measurement data ###################

df_measurements = pd.read_csv(filename_meausurementData+".csv")

print(df_measurements.head())


#for each available voltage channel in the measurement data, delete the unit behind the values in the whole column
for i in range(0,4):
    variableName = "V_CH"+str(i)
    if variableName in df_measurements.columns:
        df_measurements[variableName] = df_measurements[variableName].str.replace('V', '').astype(float)

for i in range(0,4):
    variableName = "C_CH"+str(i)
    if variableName in df_measurements.columns:
        df_measurements[variableName] = df_measurements[variableName].str.replace('A', '').astype(float)



#replace "measured value too low" or "too high" with 0 in the measured data
df_measurements['temperature'] = df_measurements['temperature'].astype(str)
df_measurements['temperature'] = df_measurements['temperature'].str.replace('measured value too low', '0')
df_measurements['temperature'] = df_measurements['temperature'].str.replace('measured value too high', '0')
df_measurements['temperature'] = df_measurements['temperature'].astype(float)

#correct the time format
df_measurements['time'] = df_measurements['time'].str.replace('T', ' ').astype(str)
df_measurements["time"] = pd.to_datetime(df_measurements["time"], format="%Y-%m-%d %H:%M:%S.%f")

#shift the timestamp by set value for alignment with other measurements
#df_measurements["time"] = df_measurements["time"] - pd.to_timedelta(0.1, unit='s')

############################################################################################


time.sleep(2)

df_measurements.to_csv(filename_meausurementData+"_data_cleaned.csv", float_format='%.16f', index=False)

time.sleep(3)

print("conversion finished")












