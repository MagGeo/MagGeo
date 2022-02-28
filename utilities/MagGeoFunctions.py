import warnings
warnings.filterwarnings('ignore', message='Could not import Cartopy package. Plotting data on maps is not available in chaosmagpy')

import sys, os
import chaosmagpy as cp
import pandas as pd
from viresclient import SwarmRequest


import utilities
from utilities.gg_to_geo import gg_to_geo
from utilities.auxiliaryfunctions import distance_to_GPS, Kradius, DistJ, DfTime_func


# 0. Get the GPS track in a CSV format.
# Input: csv file store in the data folder, validate if there is a altitute attribute.
# Output: GPS Data as pandas DF.

def getGPSData(data_dir, gpsfilename,Lat,Long,DateTime,altitude):
    
    if altitude == '':
        nfp = pd.read_csv(os.path.join(data_dir,gpsfilename), parse_dates=[0], encoding='utf-8', dayfirst=True, usecols=[Lat, Long, DateTime])
        nfp['gpsAltitude'] = 0
        nfp.rename(columns={Lat: 'gpsLat', Long: 'gpsLong', DateTime: 'gpsDateTime', altitude: 'gpsAltitude'}, inplace = True)
        # Convert the gpsDateTime to datetime python object
        nfp['gpsDateTime'] = pd.to_datetime(nfp['gpsDateTime'])
        nfp['gpsDateTime'] = nfp['gpsDateTime'].map(lambda x: x.replace(second=0))
        nfp['gpsLat'] = nfp['gpsLat'].astype(float)
        nfp['gpsLong'] = nfp['gpsLong'].astype(float)
        # Adding new column epoch, will be usefuel to compare the date&time o each gps point agains the gathered swmarm data points
        nfp['epoch'] = nfp['gpsDateTime'].astype('int64')//1e9
        nfp['epoch'] = nfp['epoch'].astype(int)
        # Computing Date and Time columns
        nfp['dates'] = nfp['gpsDateTime'].dt.date
        nfp['times'] = nfp['gpsDateTime'].dt.time
    else:
        nfp = pd.read_csv(os.path.join(data_dir,gpsfilename), parse_dates=[0], encoding='utf-8', dayfirst=True, usecols=[Lat, Long, DateTime, altitude])
        nfp.rename(columns={Lat: 'gpsLat', Long: 'gpsLong', DateTime: 'gpsDateTime', altitude: 'gpsAltitude'}, inplace = True)
        nfp.loc[(nfp['gpsAltitude'] < 0) | (nfp['gpsAltitude'].isnull()), 'gpsAltitude'] = 0
        # Convert the gpsDateTime to datetime python object
        nfp['gpsDateTime'] = pd.to_datetime(nfp['gpsDateTime'])
        nfp['gpsDateTime'] = nfp['gpsDateTime'].map(lambda x: x.replace(second=0))
        nfp['gpsLat'] = nfp['gpsLat'].astype(float)
        nfp['gpsLong'] = nfp['gpsLong'].astype(float)
        # Adding new column epoch, will be usefuel to compare the date&time o each gps point agains the gathered swmarm data points
        nfp['epoch'] = nfp['gpsDateTime'].astype('int64')//1e9
        nfp['epoch'] = nfp['epoch'].astype(int)
        # Computing Date and Time columns
        nfp['dates'] = nfp['gpsDateTime'].dt.date
        nfp['times'] = nfp['gpsDateTime'].dt.time        
    return nfp

# 1. For each day in the trayectory, Get the Swarm Data and Residuals: Get_Swarm_and_residuals
# Input:  Date and Time variables
# Output: Swarm DF for each Sat, including the residuals, and Quality Flags.

def Get_Swarm_residuals(startDateTime, endDateTime):
    
    requestA = SwarmRequest()
    requestB = SwarmRequest()
    requestC = SwarmRequest()
    
    ### 1. Request data for Sat Alpha
    requestA.set_collection("SW_OPER_MAGA_LR_1B")
    requestA.set_products(
        measurements=[
            'F', #Magnetic intensity
            'B_NEC', #The Magnetic values are in NEC system (North, East, Centre)
            'Flags_F', #Quality Flag to validate nominal values for ASM
            'Flags_B', #Quality Flag to validate nominal values for VFM, check here for more details https://earth.esa.int/web/guest/missions/esa-eo-missions/swarm/data-handbook/level-1b-product-definitions#label-Flag-Values-of-MDR_MAG_HR
        ],

        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        auxiliaries=['Kp'],
        residuals=True, #Brining the residuals.
        sampling_step="PT30S", #Get the data every 60 seconds. 
    )
   
    #Define an pandas dataframe to store the data request for Satellite A, based on the start Date and time.
    #You can display dsA to get an idea of how the data is requested.
    dsA = requestA.get_between(
        start_time=startDateTime,
        end_time=endDateTime, 
        show_progress = False,
        asynchronous = False
    ).as_dataframe(expand=True)
    ### End Request for Sat A
    
    ### 2. Request for Sat Bravo, same request parameters defined by Satelite Alpha
    requestB.set_collection("SW_OPER_MAGB_LR_1B")
    requestB.set_products(
        measurements=[
            'F', #Magnetic intensity
            'B_NEC',
            'Flags_F',
            'Flags_B',

        ],
        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        auxiliaries=['Kp'],
        residuals=True, 
        sampling_step="PT30S",
    )

    dsB = requestB.get_between(
        start_time= startDateTime,
        end_time= endDateTime,
        show_progress = False,
        asynchronous = False
    ).as_dataframe(expand=True)
    ### End Request for Sat B
    
    ## 3. Request for Sat Charlie.
    requestC.set_collection("SW_OPER_MAGC_LR_1B")
    requestC.set_products(
        measurements=[
            'F',
            'B_NEC',
            'Flags_F',
            'Flags_B',

        ],
        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        auxiliaries=['Kp'],
        residuals=True,
        sampling_step="PT30S",
    )

    dsC = requestC.get_between(
        start_time=startDateTime,
        end_time=endDateTime,
        show_progress = False,
        asynchronous = False
    ).as_dataframe(expand=True) 
    ### End Request for Sat C
    
    ##4. Renaming Geomagnetic components columns.
    dsA.rename(columns={"F_res_CHAOS_MCO_MLI_MMA":"F_res","B_NEC_res_CHAOS_MCO_MLI_MMA_N": "N_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_E":"E_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_C":"C_res"}, inplace = True)
    dsB.rename(columns={"F_res_CHAOS_MCO_MLI_MMA":"F_res","B_NEC_res_CHAOS_MCO_MLI_MMA_N": "N_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_E":"E_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_C":"C_res"}, inplace = True)
    dsC.rename(columns={"F_res_CHAOS_MCO_MLI_MMA":"F_res","B_NEC_res_CHAOS_MCO_MLI_MMA_N": "N_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_E":"E_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_C":"C_res"}, inplace = True)
    
    #5. Add the epoch column, and set that as the pandas DF index. Useful to get an ID for each date and time.
    dsA['epoch'] = dsA.index
    dsA['timestamp'] = dsA.index
    dsA['epoch'] = dsA['epoch'].astype('int64')//1e9
    dsA['epoch'] = dsA['epoch'].astype(int)
    dsA.set_index("epoch", inplace=True)
    
    dsB['epoch'] = dsB.index
    dsB['timestamp'] = dsB.index
    dsB['epoch'] = dsB['epoch'].astype('int64')//1e9
    dsB['epoch'] = dsB['epoch'].astype(int)
    dsB.set_index("epoch", inplace=True)
        
    dsC['epoch'] = dsC.index
    dsC['timestamp'] = dsC.index
    dsC['epoch'] = dsC['epoch'].astype('int64')//1e9
    dsC['epoch'] = dsC['epoch'].astype(int)
    dsC.set_index("epoch", inplace=True)

    return dsA, dsB, dsC

# 2. Filter Space and time ST-IDW based on GPS points. ST_IDW_Process
# Interpolation of the Swarm Residuals., NEC interpolated residuals for each GPS Point. Quality flags filters.
# Input:  GPS Track columns, SwarmDataDF
# Output: GPSTrack+ResidualsInterpolated

def ST_IDW_Process (GPSLat,GPSLong,GPSAltitude,GPSDateTime,GPSTime, TotalSwarmRes_A,TotalSwarmRes_B, TotalSwarmRes_C):
    
    DT=14400 #4 hours in seconds.
    # 1. Runnig the DfTime_func function to filter by the defined DeltaTime.
    time_kernel_A = DfTime_func(TotalSwarmRes_A,GPSTime,DT)
    time_kernel_B = DfTime_func(TotalSwarmRes_B,GPSTime,DT)
    time_kernel_C = DfTime_func(TotalSwarmRes_C,GPSTime,DT)
    
    #2. Computing the dt as the difference between the datetime and the datetime from swarm point. At this point
    # We have filtered the swarm point by time.
    time_kernel_A['dT'] = (GPSTime - (time_kernel_A.index))
    time_kernel_B['dT'] = (GPSTime - (time_kernel_B.index))
    time_kernel_C['dT'] = (GPSTime - (time_kernel_C.index))
    
    #3.Computing the ds
    ### Parsing the requieres parameters for distance_to_GPS function
    s_lat = GPSLat; e_lat = time_kernel_A['Latitude']; s_lng = GPSLong; e_lng = time_kernel_A['Longitude'] 
    time_kernel_A['distance']= distance_to_GPS(s_lat, s_lng, e_lat, e_lng) 
    s_lat = GPSLat; e_lat = time_kernel_B['Latitude']; s_lng = GPSLong; e_lng = time_kernel_B['Longitude']  
    time_kernel_B['distance']= distance_to_GPS(s_lat, s_lng, e_lat, e_lng)
    s_lat = GPSLat; e_lat = time_kernel_C['Latitude']; s_lng = GPSLong; e_lng = time_kernel_C['Longitude']  
    time_kernel_C['distance']= distance_to_GPS(s_lat, s_lng, e_lat, e_lng)
   
    #4. Computing the R distance.
    time_kernel_A['r']= Kradius(GPSLat)
    time_kernel_B['r']= Kradius(GPSLat)
    time_kernel_C['r']= Kradius(GPSLat)
    
    #5. Filtering rows that only fall into the computed R value.
    space_time_kA=time_kernel_A[time_kernel_A['distance']<=time_kernel_A['r']]
    space_time_kB=time_kernel_B[time_kernel_B['distance']<=time_kernel_B['r']]
    space_time_kC=time_kernel_C[time_kernel_C['distance']<=time_kernel_C['r']]
    
    ###6. Filtering Bad Points, using quality flags
    space_time_kA_res = space_time_kA[space_time_kA['F_res'].between(-2000, 2000)]
    space_time_kA_flag_F = space_time_kA_res[space_time_kA_res['Flags_F'].between(0, 1)]
    space_time_kA_res_flags = space_time_kA_flag_F[space_time_kA_flag_F['Flags_B'].between(0, 1)]

    space_time_kB_res = space_time_kB[space_time_kB['F_res'].between(-2000, 2000)]
    space_time_kB_flag_F = space_time_kB_res[space_time_kB_res['Flags_F'].between(0, 1)]
    space_time_kB_res_flags = space_time_kB_flag_F[space_time_kB_flag_F['Flags_B'].between(0, 1)]

    space_time_kC_res = space_time_kC[space_time_kC['F_res'].between(-2000, 2000)]
    space_time_kC_flag_F = space_time_kC_res[space_time_kC_res['Flags_F'].between(0, 1)]
    space_time_kC_res_flags = space_time_kC_flag_F[space_time_kC_flag_F['Flags_B'].between(0, 1)]
    
    #7. Calculating the number of points per satellite that have passed the Space and Time Windows.
    TolSatPts = (len(space_time_kA_res_flags.index)+len(space_time_kB_res_flags.index)+len(space_time_kC_res_flags.index))
    
    #8. Combining the three satellited messures into a bigger dataframe that store all the Swarm points that were filtered. 
    frames = [space_time_kA_res_flags, space_time_kB_res_flags, space_time_kC_res_flags] #List to index the specific SatId to the new full DF.
    SwarmResiduals_ST_filtered = pd.concat(frames, keys=['A', 'B','C'], sort=False)
    
    #9. Computing the minimum and average distance and the Kp index average.
    MinDistance = SwarmResiduals_ST_filtered['distance'].min()
    AvDistance = SwarmResiduals_ST_filtered['distance'].mean()
    kp_Avg = SwarmResiduals_ST_filtered['Kp'].mean()
    
    #10. Computing the d (hypotenuse compused from the edges ds, dt values
    ds = SwarmResiduals_ST_filtered['distance']
    r = SwarmResiduals_ST_filtered['r']
    dt = SwarmResiduals_ST_filtered['dT']
    SwarmResiduals_ST_filtered['Dj']= DistJ(ds, r, dt, DT)
   
    #11. Calculating the weigth values based on the previuos parameters.
    SwarmResiduals_ST_filtered['W']= 1/((SwarmResiduals_ST_filtered['Dj'])**2) #We need to make more clear this part.
    
    #12. Computing the Sum of weigths
    SumW = SwarmResiduals_ST_filtered['W'].sum()
    
    #13. Distribution of weigths
    SwarmResiduals_ST_filtered['Wj'] = SwarmResiduals_ST_filtered['W']/SumW 
    
    #14. Computing the Magnetic componente based on the weigths prevoius weigths. 
    N_res_int = (SwarmResiduals_ST_filtered['Wj']*SwarmResiduals_ST_filtered['N_res']).sum()
    E_res_int = (SwarmResiduals_ST_filtered['Wj']*SwarmResiduals_ST_filtered['E_res']).sum()
    C_res_int = (SwarmResiduals_ST_filtered['Wj']*SwarmResiduals_ST_filtered['C_res']).sum()

    #15. Write the results into an array that will be a dictionay for the final dataframe.
    resultrowGPS = {'Latitude': GPSLat, 'Longitude': GPSLong, 'Altitude': GPSAltitude, 'DateTime': GPSDateTime, 'N_res': N_res_int, 'E_res': E_res_int, 'C_res':C_res_int, 'TotalPoints':TolSatPts, 'Minimum_Distance':MinDistance, 'Average_Distance':AvDistance, 'Kp':kp_Avg}  
    return resultrowGPS

def CHAOS_ground_values(GPS_ResInt):
    
    #base_dir=os.path.dirname(os.getcwd())
    #utilities_dir = os.path.join(base_dir, "utilities")
    
    #1. Load the requiered parameters, including a local CHAOS model in mat format.
    model = cp.load_CHAOS_matfile("utilities/CHAOS-7.mat")
    theta = 90-GPS_ResInt['Latitude'].values
    phi = GPS_ResInt['Longitude'].values
    alt=GPS_ResInt['Altitude'].values
    rad_geoc_ground, theta_geoc_ground, sd_ground, cd_ground = gg_to_geo(alt, theta) # gg_to_geo, will transfor the coordinates from geocentric values to geodesic values. Altitude must be in km
    time= cp.data_utils.mjd2000(pd.DatetimeIndex(GPS_ResInt['DateTime']).year, pd.DatetimeIndex(GPS_ResInt['DateTime']).month, pd.DatetimeIndex(GPS_ResInt['DateTime']).day)
    
    #2. Compute the core, crust and magentoshpere contributions at the altitude level.
    B_r_core, B_t_core, B_phi_core = model.synth_values_tdep(time, rad_geoc_ground, theta_geoc_ground, phi) #Core Contribution
    B_r_crust, B_t_crust, B_phi_crust = model.synth_values_static(rad_geoc_ground, theta_geoc_ground, phi) #Crust Contribution
    B_r_magneto, B_t_magneto, B_phi_magneto = model.synth_values_gsm(time, rad_geoc_ground, theta_geoc_ground, phi) #Magnetosphere contribution.

    #3. Change the direcction of the axis from XYZ to r,theta and phi.
    B_r_swarm, B_t_swarm, B_phi_swarm = -GPS_ResInt['C_res'], -GPS_ResInt['N_res'], GPS_ResInt['E_res']

    #4. Compute the magnetic component (r,theta,phi) at ground level.
    B_r_ground = B_r_core + B_r_crust + B_r_magneto + B_r_swarm #(-Z)
    B_t_ground = B_t_core + B_t_crust + B_t_magneto + B_t_swarm #(-X)
    B_phi_ground = B_phi_core + B_phi_crust +B_phi_magneto + B_phi_swarm #(Y)

    #4b. Compute the CHOAS internal magnetic component (r,theta,phi) at ground level.
    B_r_ground_internal = B_r_core + B_r_crust #(-Z)
    B_t_ground_internal = B_t_core + B_t_crust #(-X)
    B_phi_ground_internal = B_phi_core + B_phi_crust #(Y)

    #5. Convert B_r_, B_t_, and B_phi to XYZ (NEC)
    Z_chaos = -B_r_ground   #Z
    X_chaos = -B_t_ground   #X
    Y_chaos = B_phi_ground  #Y

    #5b. Convert full field with CHOAS internal only B_r_, B_t_, and B_phi to XYZ (NEC)
    Z_chaos_internal = -B_r_ground_internal #Z
    X_chaos_internal = -B_t_ground_internal #X
    Y_chaos_internal = B_phi_ground_internal #Y

    #6. Rotate the X(N) and Z(C) magnetic field values of the chaos models into the geodectic frame using the sd and cd (sine and cosine d from gg_to_geo) 
    X_obs = X_chaos*cd_ground + Z_chaos*sd_ground #New N
    Z_obs = Z_chaos*cd_ground - X_chaos*sd_ground #New C
    Y_obs = Y_chaos # New E

    #6b. Rotate the X(N) and Z(C) magnetic field values of the internal part of chaos models into the geodetic frame using the sd and cd (sine and cosine d from gg_to_geo) 
    X_obs_internal = X_chaos_internal *cd_ground + Z_chaos_internal*sd_ground #New N
    Z_obs_internal = Z_chaos_internal *cd_ground - X_chaos_internal*sd_ground #New C
    Y_obs_internal = Y_chaos_internal # New E

    return X_obs, Y_obs, Z_obs, X_obs_internal, Y_obs_internal, Z_obs_internal