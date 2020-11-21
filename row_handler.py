import pandas as pd
import numpy as np
import os
from MagGeoFunctions import ST_IDW_Process
from MagGeoFunctions import CHAOS_ground_values


def row_handler (GPSData):
    dn = [] ## List used to add all the GPS points with the annotated MAG Data. See the last bullet point of this process        
    for index, row in GPSData.iterrows():
        GPSLat = row['gpsLat']
        GPSLong = row['gpsLong']
        GPSDateTime = row['gpsDateTime']
        GPSTime = row['epoch']
        GPSAltitude = row['gpsAltitude']
        print("Process for:", index,"Date&Time:",GPSDateTime, "Epoch", GPSTime)
        try:
            result=ST_IDW_Process(GPSLat,GPSLong,GPSAltitude,GPSDateTime,GPSTime)
            dn.append(result)
        except:
            print("Ups!.That was a bad Swarm Point, let's keep working with the next point")
            result_badPoint= {'Latitude': GPSLat, 'Longitude': GPSLong, 'Altitude':GPSAltitude, 'DateTime': GPSDateTime, 'N_res': np.nan, 'E_res': np.nan, 'C_res':np.nan, 'TotalPoints':0, 'Minimum_Distance':np.nan, 'Average_Distance':np.nan}  
            dn.append(result_badPoint)
            continue

    GPS_ResInt = pd.DataFrame(dn)
    X_obs, Y_obs, Z_obs =CHAOS_ground_values(GPS_ResInt)
    GPS_ResInt['N'] =pd.Series(X_obs)
    GPS_ResInt['E'] =pd.Series(Y_obs)
    GPS_ResInt['C'] =pd.Series(Z_obs)
    GPS_ResInt.drop(columns=['N_res', 'E_res','C_res'], inplace=True)
    return GPS_ResInt