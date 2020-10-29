import chaosmagpy as cp
import pandas as pd
from chaosmagpy import load_CHAOS_matfile
from chaosmagpy.data_utils import mjd2000
from viresclient import SwarmRequest
import sys,os

from gg_to_geo import gg_to_geo
from auxiliaryfunctions import distance_to_GPS, Kradius, DistJ, DfTime_func

# 1. Every Day, Get the Swarm Data and Residuals: Get_Swarm_and_residuals
# Filter the Bad Ones
# Input:  Time variables
# Output: Swarm DF, including the residuals, ABC combined.

def Get_Swarm_residuals(startDateTime, endDateTime):
    
    requestA = SwarmRequest() 
    requestB = SwarmRequest()
    requestC = SwarmRequest()
    ### Request for Sat A
    requestA.set_collection("SW_OPER_MAGA_LR_1B")
    requestA.set_products(
        measurements=[
            'F', #Magnetic intensity
            'B_NEC', #The Magnetic values are in NEC system (North, East, Centre)

        ],

        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        auxiliaries=['Kp'],
        residuals=True, #Brining the residuals.
        sampling_step="PT60S", #Get the data every 60 seconds. 
    )
    
    #Define an array to store the data request for Satellite A, based on the start Date and time.
    #You can display dsA to get an idea of how the data is requested.
    dsA = requestA.get_between(
        start_time=startDateTime,
        end_time=endDateTime
    ).as_dataframe()
           
    ### End Request for Sat A
    
    ### Request for Sat B
    requestB.set_collection("SW_OPER_MAGB_LR_1B")
    requestB.set_products(
        measurements=[
            'F', #Magnetic intensity
            'B_NEC',

        ],
        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        auxiliaries=['Kp'],
        residuals=True, 
        sampling_step="PT60S",
    )

    dsB = requestB.get_between(
        start_time= startDateTime,
        end_time= endDateTime
    ).as_dataframe()
    ### End Request for Sat B
    ### Request for Sat C
    requestC.set_collection("SW_OPER_MAGC_LR_1B")
    requestC.set_products(
        measurements=[
            'F',
            'B_NEC',

        ],
        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        auxiliaries=['Kp'],
        residuals=True,
        sampling_step="PT60S",
    )

    dsC = requestC.get_between(
        start_time=startDateTime,
        end_time=endDateTime
    ).as_dataframe()
    ### End Request for Sat C
    dsA[['N_res','E_res','C_res']] = pd.DataFrame(dsA.B_NEC_res_CHAOS_MCO_MLI_MMA.tolist(), index= dsA.index)
    dsA.drop(columns=['B_NEC_res_CHAOS_MCO_MLI_MMA'], inplace=True)
    dsB[['N_res','E_res','C_res']] = pd.DataFrame(dsB.B_NEC_res_CHAOS_MCO_MLI_MMA.tolist(), index= dsB.index)
    dsB.drop(columns=['B_NEC_res_CHAOS_MCO_MLI_MMA'], inplace=True)
    dsC[['N_res','E_res','C_res']] = pd.DataFrame(dsC.B_NEC_res_CHAOS_MCO_MLI_MMA.tolist(), index= dsC.index)
    dsC.drop(columns=['B_NEC_res_CHAOS_MCO_MLI_MMA'], inplace=True)
    #Remove the "bad Swarm" points in a range of -+ 2.000 nT
    dsA_filtered = dsA[dsA['F_res_CHAOS_MCO_MLI_MMA'].between(-2000, 2000)]
    dsB_filtered = dsB[dsB['F_res_CHAOS_MCO_MLI_MMA'].between(-2000, 2000)]
    dsC_filtered = dsC[dsA['F_res_CHAOS_MCO_MLI_MMA'].between(-2000, 2000)]

    dsA_filtered['epoch'] = dsA_filtered.index
    dsA_filtered['timestamp'] = dsA_filtered.index
    dsA_filtered['epoch'] = dsA_filtered['epoch'].astype('int64')//1e9
    dsA_filtered['epoch'] = dsA_filtered['epoch'].astype(int)
    dsA_filtered.set_index("epoch", inplace=True)
    
    dsB_filtered['epoch'] = dsB_filtered.index
    dsB_filtered['timestamp'] = dsB_filtered.index
    dsB_filtered['epoch'] = dsB_filtered['epoch'].astype('int64')//1e9
    dsB_filtered['epoch'] = dsB_filtered['epoch'].astype(int)
    dsB_filtered.set_index("epoch", inplace=True)
    
    dsC_filtered['epoch'] = dsC_filtered.index
    dsC_filtered['timestamp'] = dsC_filtered.index
    dsC_filtered['epoch'] = dsC_filtered['epoch'].astype('int64')//1e9
    dsC_filtered['epoch'] = dsC_filtered['epoch'].astype(int)
    dsC_filtered.set_index("epoch", inplace=True)

    return dsA_filtered, dsB_filtered, dsC_filtered

# 2. Filter Space and time ST-IDW based on GPS points. ST_IDW_Process
# Interpolation of the Swarm Residuals., NEC interpolated residuals for each GPS Point.
# Input:  GPS Track columns, SwarmDataDF
# Output: GPSTrack+ResidualsInterpolated

SwarmDir= os.chdir(r"../temp_data")

TotalSwarmRes_A = pd.read_csv('TotalSwarmRes_A.csv',low_memory=False, index_col='epoch')
TotalSwarmRes_B = pd.read_csv('TotalSwarmRes_B.csv',low_memory=False, index_col='epoch')
TotalSwarmRes_C = pd.read_csv('TotalSwarmRes_C.csv',low_memory=False, index_col='epoch')


def ST_IDW_Process (GPSLat,GPSLong,GPSAltitude,GPSDateTime,GPSTime):
    DT=14400
    # 1. Runnig the DfTime_func function to filter by the defined Delta Time.
    time_kernel_A = DfTime_func(TotalSwarmRes_A,GPSTime,DT)
    time_kernel_B = DfTime_func(TotalSwarmRes_B,GPSTime,DT)
    time_kernel_C = DfTime_func(TotalSwarmRes_C,GPSTime,DT)
    #2. Computing the dt as the difference between the datetime and the datetime from swarm point. At this point
    #   we have filtered the swarm point by time.
    time_kernel_A['dT'] = (GPSTime - (time_kernel_A.index))
    time_kernel_B['dT'] = (GPSTime - (time_kernel_B.index))
    time_kernel_C['dT'] = (GPSTime - (time_kernel_C.index))
    
    #3.Computing the ds
    # 3.1 Parsing the requieres parameters for distance_to_GPS function
    s_lat = GPSLat; e_lat = time_kernel_A['Latitude']; s_lng = GPSLong; e_lng = time_kernel_A['Longitude']
    
    ## Running the function, based on the previous parameters, for SatA
    time_kernel_A['distance']= distance_to_GPS(s_lat, s_lng, e_lat, e_lng) 
    
    s_lat = GPSLat; e_lat = time_kernel_B['Latitude']; s_lng = GPSLong; e_lng = time_kernel_B['Longitude']  
    # Running the function, based on the previous parameters, for SatB
    time_kernel_B['distance']= distance_to_GPS(s_lat, s_lng, e_lat, e_lng)
    
    s_lat = GPSLat; e_lat = time_kernel_C['Latitude']; s_lng = GPSLong; e_lng = time_kernel_C['Longitude']  
    # Running the function, based on the previous parameters, for SatC
    time_kernel_C['distance']= distance_to_GPS(s_lat, s_lng, e_lat, e_lng) 
    
    #3.2 Computing the R distance.
    time_kernel_A['r']= Kradius(GPSLat)
    time_kernel_B['r']= Kradius(GPSLat)
    time_kernel_C['r']= Kradius(GPSLat)
    
    #3.3 Filtering row that only fall into the computed R value.
    space_time_kA=time_kernel_A[time_kernel_A['distance']<=time_kernel_A['r']]
    space_time_kB=time_kernel_B[time_kernel_B['distance']<=time_kernel_B['r']]
    space_time_kC=time_kernel_C[time_kernel_C['distance']<=time_kernel_C['r']]
    
    #4. Calculating the number of points per satellite that have passed the Space and Time Windows.
    NumPointsA = len(space_time_kA.index)
    NumPointsB = len(space_time_kB.index)
    NumPointsC = len(space_time_kC.index)
    TolSatPts = (NumPointsA+NumPointsB+NumPointsC)
    
    #5. Combining the three satellited messures into a bigger dataframe that store all the Swarm points that were filtered. 
    frames = [space_time_kA, space_time_kB, space_time_kC] #List to index the specific SatId to the new full DF.
    SwarmResiduals_ST_filtered = pd.concat(frames, keys=['A', 'B', 'C'], sort=False)
    
    #6. Computing the minimum and average distance and the Kp index average.
    MinDistance = SwarmResiduals_ST_filtered['distance'].min()
    AvDistance = SwarmResiduals_ST_filtered['distance'].mean()
    kp_Avg = SwarmResiduals_ST_filtered['Kp'].mean()
    
    #7. Computing the d (hypotenuse compused from the edges ds, dt values
    ds = SwarmResiduals_ST_filtered['distance']
    r = SwarmResiduals_ST_filtered['r']
    dt = SwarmResiduals_ST_filtered['dT']
    SwarmResiduals_ST_filtered['Dj']= DistJ(ds, r, dt, DT)
   
    #8 Calculating the weigth values based on the previuos parameters.
    SwarmResiduals_ST_filtered['W']= 1/((SwarmResiduals_ST_filtered['Dj'])**2) #We need to make more clear this part.
    
    #9. Computing the Sum of weigths
    SumW = SwarmResiduals_ST_filtered['W'].sum()
    #10. Distribution of weigths
    SwarmResiduals_ST_filtered['Wj'] = SwarmResiduals_ST_filtered['W']/SumW 
    #Could be  some bias. So we need to find a way to apply this weigth maybe base on distance and time using DT (4hrs)
    
    #11. Computing the Magnetic componente based on the weigths prevoius weigths. 
    N_res_int = (SwarmResiduals_ST_filtered['Wj']*SwarmResiduals_ST_filtered['N_res']).sum()
    E_res_int = (SwarmResiduals_ST_filtered['Wj']*SwarmResiduals_ST_filtered['E_res']).sum()
    C_res_int = (SwarmResiduals_ST_filtered['Wj']*SwarmResiduals_ST_filtered['C_res']).sum()

    #12. Write the results into an array that will be a dictionay for the final dataframe.
    resultrowGPS = {'Latitude': GPSLat, 'Longitude': GPSLong, 'Altitude': GPSAltitude, 'DateTime': GPSDateTime, 'N_res': N_res_int, 'E_res': E_res_int, 'C_res':C_res_int, 'TotalPoints':TolSatPts, 'Minimum_Distance':MinDistance, 'Average_Distance':AvDistance, 'Kp':kp_Avg}  
    return resultrowGPS

def CHAOS_ground_values(GPS_ResInt):
    
    model = load_CHAOS_matfile('C:\\foss4guk19-jupyter-master\\Project_StAndrews\\Parallel\\CHAOS-7.mat')
    theta = 90-GPS_ResInt['Latitude'].values
    phi = GPS_ResInt['Longitude'].values
    alt=GPS_ResInt['Altitude'].values
    rad_geoc_ground, theta_geoc_ground, sd_ground, cd_ground = gg_to_geo(alt, theta) #altitude in km
    time= mjd2000(pd.DatetimeIndex(GPS_ResInt['DateTime']).year, pd.DatetimeIndex(GPS_ResInt['DateTime']).month, pd.DatetimeIndex(GPS_ResInt['DateTime']).day)

    B_r_core, B_t_core, B_phi_core = model.synth_values_tdep(time, rad_geoc_ground, theta_geoc_ground, phi) #Core Contribution
    B_r_crust, B_t_crust, B_phi_crust = model.synth_values_static(rad_geoc_ground, theta_geoc_ground, phi) #Crust Contribution
    B_r_magneto, B_t_magneto, B_phi_magneto = model.synth_values_gsm(time, rad_geoc_ground, theta_geoc_ground, phi) #Magnetosphere contribution.

    #Change the direcction of the axis from XYZ to r,theta and phi.
    B_r_swarm, B_t_swarm, B_phi_swarm = -GPS_ResInt['C_res'], -GPS_ResInt['N_res'], GPS_ResInt['E_res']


    #Compute the magnetic component (r,theta,phi) at ground level.
    B_r_ground = B_r_core + B_r_crust + B_r_magneto + B_r_swarm #(-Z)
    B_t_ground = B_t_core + B_t_crust + B_t_magneto + B_t_swarm #(-X)
    B_phi_ground = B_phi_core + B_phi_crust +B_phi_magneto + B_phi_swarm #(Y)

    #Convert B_r_, B_t_, and B_phi to XYZ (NEC)
    Z_chaos = -B_r_ground   #Z
    X_chaos = -B_t_ground   #X
    Y_chaos = B_phi_ground  #Y

    #Rotate the X(N) and Z(C) magnetic field values of the chaos models into the geodectic frame using the sd and cd (sine and cosine d from gg_to_geo) 
    X_obs = X_chaos*cd_ground + Z_chaos*sd_ground #New N
    Z_obs = Z_chaos*cd_ground - X_chaos*sd_ground #New C
    Y_obs = Y_chaos # New E
    return X_obs, Y_obs, Z_obs