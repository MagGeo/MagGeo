import pandas as pd
import numpy as np
import sys, os
from pathlib import Path
from tqdm import tqdm
import utilities
from utilities.MagGeoFunctions import ST_IDW_Process
from utilities.MagGeoFunctions import CHAOS_ground_values

base_dir = str(Path(os.getcwd()).parent)  # Get main MagGeo directory (should be parent to this file)
temp_results_dir = os.path.join(base_dir, "temp_data")
utilities_dir = os.path.join(base_dir, "utilites")

TotalSwarmRes_A = pd.read_csv(os.path.join(temp_results_dir,"TotalSwarmRes_A.csv"),low_memory=False, index_col='epoch')
TotalSwarmRes_A['timestamp'] = pd.to_datetime(TotalSwarmRes_A['timestamp'])
TotalSwarmRes_B = pd.read_csv(os.path.join(temp_results_dir,"TotalSwarmRes_B.csv"),low_memory=False, index_col='epoch')
TotalSwarmRes_B['timestamp'] = pd.to_datetime(TotalSwarmRes_B['timestamp'])
TotalSwarmRes_C = pd.read_csv(os.path.join(temp_results_dir,"TotalSwarmRes_C.csv"),low_memory=False, index_col='epoch')
TotalSwarmRes_C['timestamp'] = pd.to_datetime(TotalSwarmRes_C['timestamp'])

def row_handler (GPSData):
    dn = [] ## List used to add all the GPS points with the annotated MAG Data. See the last bullet point of this process        
    for index, row in tqdm(GPSData.iterrows(), total=GPSData.shape[0], desc="Annotating the GPS Trayectory"):
        GPSLat = row['gpsLat']
        GPSLong = row['gpsLong']
        GPSDateTime = row['gpsDateTime']
        GPSTime = row['epoch']
        GPSAltitude = row['gpsAltitude']
        #print("Process for:", index,"Date&Time:",GPSDateTime, "Epoch", GPSTime)
        try:
            result=ST_IDW_Process(GPSLat,GPSLong,GPSAltitude, GPSDateTime,GPSTime, TotalSwarmRes_A, TotalSwarmRes_B, TotalSwarmRes_C)
            dn.append(result)
        except:
            #print("Ups!.That was a bad Swarm Point, let's keep working with the next point")
            result_badPoint= {'Latitude': GPSLat, 'Longitude': GPSLong, 'Altitude':GPSAltitude, 'DateTime': GPSDateTime, 'N_res': np.nan, 'E_res': np.nan, 'C_res':np.nan, 'TotalPoints':0, 'Minimum_Distance':np.nan, 'Average_Distance':np.nan}  
            dn.append(result_badPoint)
            continue

    
    GPS_ResInt = pd.DataFrame(dn)
    GPS_ResInt.to_csv (os.path.join(temp_results_dir,"GPS_ResInt.csv"), header=True)

    X_obs, Y_obs, Z_obs, X_obs_internal, Y_obs_internal, Z_obs_internal =CHAOS_ground_values(utilities_dir,GPS_ResInt)
    GPS_ResInt['N'] =pd.Series(X_obs)
    GPS_ResInt['E'] =pd.Series(Y_obs)
    GPS_ResInt['C'] =pd.Series(Z_obs)
    GPS_ResInt['N_Obs'] =pd.Series(X_obs_internal)
    GPS_ResInt['E_Obs'] =pd.Series(Y_obs_internal)
    GPS_ResInt['C_Obs'] =pd.Series(Z_obs_internal)

    GPS_ResInt.drop(columns=['N_res', 'E_res','C_res'], inplace=True)

    return GPS_ResInt