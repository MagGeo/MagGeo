import warnings

import pandas as pd
import numpy as np
import sys, os
import chaosmagpy as cp
from pathlib import Path
from tqdm import tqdm
from .auxiliaryfunctions import ST_IDW_Process, gg_to_geo

# Get main MagGeo directory (should be parent to this file)
base_dir=os.path.dirname(os.getcwd())
temp_results_dir = os.path.join(base_dir, "temp_data")

TotalSwarmRes_A = pd.read_csv(os.path.join(temp_results_dir,"TotalSwarmRes_A.csv"),low_memory=False, index_col='epoch')
TotalSwarmRes_A['timestamp'] = pd.to_datetime(TotalSwarmRes_A['timestamp'])
TotalSwarmRes_B = pd.read_csv(os.path.join(temp_results_dir,"TotalSwarmRes_B.csv"),low_memory=False, index_col='epoch')
TotalSwarmRes_B['timestamp'] = pd.to_datetime(TotalSwarmRes_B['timestamp'])
TotalSwarmRes_C = pd.read_csv(os.path.join(temp_results_dir,"TotalSwarmRes_C.csv"),low_memory=False, index_col='epoch')
TotalSwarmRes_C['timestamp'] = pd.to_datetime(TotalSwarmRes_C['timestamp'])

def row_handler (GPSData):
    dn = [] ## List used to add all the GPS points with the annotated MAG Data. See the last bullet point of this process        
    for index, row in tqdm(GPSData.iterrows(), total=GPSData.shape[0], desc="Annotating the GPS Trajectory"):
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

    def CHAOS_ground_values(GPS_ResInt):
        
        base_dir=os.path.dirname(os.getcwd())
        utilities_dir = os.path.join(base_dir, "utilities")
        
        #1. Load the required parameters, including a local CHAOS model in mat format.
        model = cp.load_CHAOS_matfile(os.path.join(utilities_dir,'CHAOS-7.mat'))
        theta = 90-GPS_ResInt['Latitude'].values
        phi = GPS_ResInt['Longitude'].values
        alt=GPS_ResInt['Altitude'].values
        rad_geoc_ground, theta_geoc_ground, sd_ground, cd_ground = gg_to_geo(alt, theta) # gg_to_geo, will transform the coordinates from geocentric values to geodesic values. Altitude must be in km
        time= cp.data_utils.mjd2000(pd.DatetimeIndex(GPS_ResInt['DateTime']).year, pd.DatetimeIndex(GPS_ResInt['DateTime']).month, pd.DatetimeIndex(GPS_ResInt['DateTime']).day)
        
        #2. Compute the core, crust and magnetosphere contributions at the altitude level.
        B_r_core, B_t_core, B_phi_core = model.synth_values_tdep(time, rad_geoc_ground, theta_geoc_ground, phi) #Core Contribution
        B_r_crust, B_t_crust, B_phi_crust = model.synth_values_static(rad_geoc_ground, theta_geoc_ground, phi) #Crust Contribution
        B_r_magneto, B_t_magneto, B_phi_magneto = model.synth_values_gsm(time, rad_geoc_ground, theta_geoc_ground, phi) #Magnetosphere contribution.

        #3. Change the direction of the axis from XYZ to r,theta and phi.
        B_r_swarm, B_t_swarm, B_phi_swarm = -GPS_ResInt['C_res'], -GPS_ResInt['N_res'], GPS_ResInt['E_res']

        #4. Compute the magnetic component (r,theta,phi) at ground level.
        B_r_ground = B_r_core + B_r_crust + B_r_magneto + B_r_swarm #(-Z)
        B_t_ground = B_t_core + B_t_crust + B_t_magneto + B_t_swarm #(-X)
        B_phi_ground = B_phi_core + B_phi_crust +B_phi_magneto + B_phi_swarm #(Y)

        #4b. Compute the CHAOS internal magnetic component (r,theta,phi) at ground level.
        B_r_ground_internal = B_r_core + B_r_crust #(-Z)
        B_t_ground_internal = B_t_core + B_t_crust #(-X)
        B_phi_ground_internal = B_phi_core + B_phi_crust #(Y)

        #5. Convert B_r_, B_t_, and B_phi to XYZ (NEC)
        Z_chaos = -B_r_ground   #Z
        X_chaos = -B_t_ground   #X
        Y_chaos = B_phi_ground  #Y

        #5b. Convert full field with CHAOS internal only B_r_, B_t_, and B_phi to XYZ (NEC)
        Z_chaos_internal = -B_r_ground_internal #Z
        X_chaos_internal = -B_t_ground_internal #X
        Y_chaos_internal = B_phi_ground_internal #Y

        #6. Rotate the X(N) and Z(C) magnetic field values of the chaos models into the geodetic frame using the sd and cd (sine and cosine d from gg_to_geo) 
        X_obs = X_chaos*cd_ground + Z_chaos*sd_ground #New N
        Z_obs = Z_chaos*cd_ground - X_chaos*sd_ground #New C
        Y_obs = Y_chaos # New E

        #6b. Rotate the X(N) and Z(C) magnetic field values of the internal part of CHAOS models into the geodetic frame using the sd and cd (sine and cosine d from gg_to_geo) 
        X_obs_internal = X_chaos_internal *cd_ground + Z_chaos_internal*sd_ground #New N
        Z_obs_internal = Z_chaos_internal *cd_ground - X_chaos_internal*sd_ground #New C
        Y_obs_internal = Y_chaos_internal # New E

        return X_obs, Y_obs, Z_obs, X_obs_internal, Y_obs_internal, Z_obs_internal

    X_obs, Y_obs, Z_obs, X_obs_internal, Y_obs_internal, Z_obs_internal =CHAOS_ground_values(GPS_ResInt)

    GPS_ResInt['N'] =pd.Series(X_obs)
    GPS_ResInt['E'] =pd.Series(Y_obs)
    GPS_ResInt['C'] =pd.Series(Z_obs)
    GPS_ResInt['N_Obs'] =pd.Series(X_obs_internal)
    GPS_ResInt['E_Obs'] =pd.Series(Y_obs_internal)
    GPS_ResInt['C_Obs'] =pd.Series(Z_obs_internal)

    GPS_ResInt.drop(columns=['N_res', 'E_res','C_res'], inplace=True)

    return GPS_ResInt