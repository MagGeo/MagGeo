import chaosmagpy as cp
import pandas as pd
from chaosmagpy import load_CHAOS_matfile
from chaosmagpy.data_utils import mjd2000
from gg_to_geo import gg_to_geo

def GetSwarmData_and_ionosphereCorrect(startDateTime, endDateTime, mid_date):
    
    # 1. Starting the Swarm Request.
    #    `SwarmRequest` is an object provided by the VirES interface, we need time objects 
    #    to be used by `SwarmRequest.get_between()` in this case we will get every date one day per loop (i.e. around 15 orbits)
    #    of the scalar (`F`) measurements from Swarm Satellites. The data are then loaded as a `xarray` dataframe.
    #    donwsamples the data to 60 seconds, from the `MAGx_LR` product having default of 1 second.
    #    https://viresclient.readthedocs.io/en/latest/available_parameters.html
    
    requestA = SwarmRequest() 
    requestB = SwarmRequest()
    requestC = SwarmRequest()
    
    #2. Loading the matlab CHAOS model to compute the residuals and resting those values from the residuals from Swarm.
    model = load_CHAOS_matfile('C:\\foss4guk19-jupyter-master\\Project_StAndrews\\Parallel\\CHAOS-7.mat') 
    #For more information about the magnetic models go to: 
    #https://www.space.dtu.dk/english/research/scientific_data_and_models/magnetic_field_models
    
    #3. Get the data for Sat A,make the ionosphere correction and compute the mag values at the ground level
    
    ######Request for Sat A #########
    requestA.set_collection("SW_OPER_MAGA_LR_1B")
    requestA.set_products(
        measurements=[
            'F', #Magnetic intensity
            'B_NEC', #The Magnetic values are in NEC system (North, East, Centre)

        ],

        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        residuals=True, #Brining the residuals.
        sampling_step="PT60S", #Get the data every 60 seconds. 
    )
    
    #Define an array to store the data request for Satellite A, based on the start Date and time.
    #You can display dsA to get an idea of how the data is requested.
    dsA = requestA.get_between(
        start_time=startDateTime,
        end_time=endDateTime
    ).as_xarray()
    
    
    #Compute the theta, phi and radial magnetic components from CHAOS, for Sat A.
    
    thetaA = 90-dsA["Latitude"].values  # colatitude in degrees (colatitude = 90-latitude)
    #If you need to add the heigth of your GPS trajectory, you need to put in the bird's height in km as the firts
    #paramter of gg_to_geo function.For this example 0 means at the sea level. 
    #The radius will be different for each location even if it is at ‘sea level’ or wgs84 elliposoid
    rad_geoc_groundA, theta_geoc_groundA, sd_groundA, cd_groundA = gg_to_geo(0, thetaA) 
    phiA = dsA["Longitude"].values  # longitude in degrees
    # The core field does not change over a day, so we pick the processed day
    timeA = mjd2000(mid_date.year, mid_date.month, mid_date.day)  * np.ones((thetaA.size,))
    
    # Compute the Core, Crust, Magnetosphere at the ground level for the r_ theta and Phi components.
    B_r_coreA, B_t_coreA, B_phi_coreA = model.synth_values_tdep(timeA, rad_geoc_groundA, theta_geoc_groundA, phiA) #Core contribution
    B_r_crustA, B_t_crustA, B_phi_crustA = model.synth_values_static(rad_geoc_groundA, theta_geoc_groundA, phiA) #Crust Contribution
    B_r_magnetoA, B_t_magnetoA, B_phi_magnetoA = model.synth_values_gsm(timeA, rad_geoc_groundA, theta_geoc_groundA, phiA) #Magnetosphere contribution.

    #Change the direcction of the axis from XYZ to r,theta and phi.
    B_r_swarmA, B_t_swarmA, B_phi_swarmA = -dsA["B_NEC_res_CHAOS_MCO_MLI_MMA"][:, 2], -dsA["B_NEC_res_CHAOS_MCO_MLI_MMA"][:, 0], dsA["B_NEC_res_CHAOS_MCO_MLI_MMA"][:, 1]

    #Get the residuals from F, we will use those valuse to identify the Swarm Bad Points.
    Fa_res = dsA["F_res_CHAOS_MCO_MLI_MMA"]

    #Compute the magnetic component (r,theta,phi) at ground level.
    B_r_groundA = B_r_coreA + B_r_crustA + B_r_magnetoA + B_r_swarmA #(-Z)
    B_t_groundA = B_t_coreA + B_t_crustA + B_t_magnetoA + B_t_swarmA #(-X)
    B_phi_groundA = B_phi_coreA + B_phi_crustA +B_phi_magnetoA + B_phi_swarmA #(Y)


    #Convert B_r_, B_t_, and B_phi to XYZ (NEC)
    Z_chaosA = -B_r_groundA   #Z
    X_chaosA = -B_t_groundA   #X
    Y_chaosA = B_phi_groundA  #Y, or New E

    #Rotate the X(N) and Z(C) magnetic field values of the chaos models into the geodectic frame using the sd and cd (sine and cosine d from gg_to_geo) 
    X_obsA = X_chaosA*cd_groundA + Z_chaosA*sd_groundA #New N
    Z_obsA = Z_chaosA*cd_groundA - X_chaosA*sd_groundA #New C
    Y_obsA = Y_chaosA    
    #Write the results to a new pandas DataFrame. 

    SwarmDataA = pd.DataFrame({'F_res':Fa_res, 'Na':X_obsA,'Ea':Y_obsA, 'Ca':Z_obsA, 'Ta':X_obsA['Timestamp'], 'LatA':dsA['Latitude'], 'LongA':dsA['Longitude']})
    SwarmDataA['epoch'] = SwarmDataA['Ta'].astype('int64')//1e9
    SwarmDataA['epoch'] = SwarmDataA['epoch'].astype(int)
    SwarmDataA.set_index("epoch", inplace=True)
    ### End of Sat A request and process#####

    #4. Get the data for Sat B,make the ionosphere correction and compute the mag values at the ground level
    
    ######Request for Sat B #########
    requestB.set_collection("SW_OPER_MAGB_LR_1B")
    requestB.set_products(
        measurements=[
            'F', #Magnetic intensity
            'B_NEC',

        ],
        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        residuals=True, 
        sampling_step="PT60S",
    )

    dsB = requestB.get_between(
        start_time= startDateTime,
        end_time= endDateTime
    ).as_xarray()
    
    thetaB = 90-dsB["Latitude"].values  # colatitude in degrees (colatitude = 90-latitude)
    rad_geoc_groundB, theta_geoc_groundB, sd_groundB, cd_groundB = gg_to_geo(0, thetaB) 
    phiB = dsB["Longitude"].values  # longitude in degrees
    # The core field does not change over a day, so we pick the processed day
    timeB = mjd2000(mid_date.year, mid_date.month, mid_date.day)  * np.ones((thetaA.size,))
    
    B_r_coreB, B_t_coreB, B_phi_coreB = model.synth_values_tdep(timeB,rad_geoc_groundB, theta_geoc_groundB, phiB) #Crust Contributions
    B_r_crustB, B_t_crustB, B_phi_crustB = model.synth_values_static(rad_geoc_groundB, theta_geoc_groundB, phiB) #Crust Contribitions
    B_r_magnetoB, B_t_magnetoB, B_phi_magnetoB = model.synth_values_gsm(timeB, rad_geoc_groundB, theta_geoc_groundB, phiB) #Magnetosphere Contributions
    
    B_r_swarmB, B_t_swarmB, B_phi_swarmB = -dsB["B_NEC_res_CHAOS_MCO_MLI_MMA"][:, 2], -dsB["B_NEC_res_CHAOS_MCO_MLI_MMA"][:, 0], dsB["B_NEC_res_CHAOS_MCO_MLI_MMA"][:, 1]
    Fb_res = dsB["F_res_CHAOS_MCO_MLI_MMA"]

    B_r_groundB = B_r_coreB + B_r_crustB + B_r_magnetoB + B_r_swarmB #(-Z)
    B_t_groundB = B_t_coreB + B_t_crustB + B_t_magnetoB + B_t_swarmB #(-X)
    B_phi_groundB = B_phi_coreB + B_phi_crustB + B_phi_magnetoB + B_phi_swarmB #(Y)
    
    Z_chaosB = -B_r_groundB   #Z
    X_chaosB = -B_t_groundB   #X
    Y_chaosB = B_phi_groundB  #Y
    
    X_obsB = X_chaosB*cd_groundB + Z_chaosB*sd_groundB #New N
    Z_obsB = Z_chaosB*cd_groundB - X_chaosB*sd_groundB #New C
    Y_obsB = Y_chaosB #New E
    
    
    SwarmDataB = pd.DataFrame({'F_res':Fb_res,'Nb':X_obsB,'Eb':Y_obsB, 'Cb':Z_obsB, 'Tb':X_obsB['Timestamp'], 'LatB':dsB['Latitude'], 'LongB':dsB['Longitude']})
    SwarmDataB['epoch'] = SwarmDataB['Tb'].astype('int64')//1e9
    SwarmDataB['epoch'] = SwarmDataB['epoch'].astype(int)
    SwarmDataB.set_index("epoch", inplace=True)
    ### End of Sat B request and process#####
    
    #5. Get the data for Sat C,make the ionosphere correction and compute the mag values at the ground level
    
    ######Request for Sat C #########
    requestC.set_collection("SW_OPER_MAGC_LR_1B")
    requestC.set_products(
        measurements=[
            'F',
            'B_NEC',

        ],
        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        residuals=True,
        sampling_step="PT60S",
    )

    dsC = requestC.get_between(
        start_time=startDateTime,
        end_time=endDateTime
    ).as_xarray()
    
    
    thetaC = 90-dsC["Latitude"].values  # colatitude in degrees (colatitude = 90-latitude)
    rad_geoc_groundC, theta_geoc_groundC, sd_groundC, cd_groundC = gg_to_geo(0, thetaC) 
    phiC = dsC["Longitude"].values  # longitude in degrees
    timeC = mjd2000(mid_date.year, mid_date.month, mid_date.day)  * np.ones((thetaC.size,))

    B_r_coreC, B_t_coreC, B_phi_coreC = model.synth_values_tdep(timeC,rad_geoc_groundC, theta_geoc_groundC, phiC)
    B_r_crustC, B_t_crustC, B_phi_crustC = model.synth_values_static(rad_geoc_groundC, theta_geoc_groundC, phiC)
    B_r_magnetoC, B_t_magnetoC, B_phi_magnetoC = model.synth_values_gsm(timeC, rad_geoc_groundC, theta_geoc_groundC, phiC)
    
    B_r_swarmC, B_t_swarmC, B_phi_swarmC = -dsC["B_NEC_res_CHAOS_MCO_MLI_MMA"][:, 2], -dsC["B_NEC_res_CHAOS_MCO_MLI_MMA"][:, 0], dsC["B_NEC_res_CHAOS_MCO_MLI_MMA"][:, 1]
    Fc_res = dsC["F_res_CHAOS_MCO_MLI_MMA"]
    
    B_r_groundC = B_r_coreC+ B_r_crustC + B_r_magnetoC + B_r_swarmC #(-Z)
    B_t_groundC = B_t_coreC + B_t_crustC + B_t_magnetoC + B_t_swarmC #(-X)
    B_phi_groundC = B_phi_coreC + B_phi_crustC + B_phi_magnetoC + B_phi_swarmC #(Y)
    
    Z_chaosC = -B_r_groundC   #Z
    X_chaosC = -B_t_groundC   #X
    Y_chaosC = B_phi_groundC  #Y
    
    X_obsC = X_chaosC*cd_groundC + Z_chaosC*sd_groundC #New N
    Z_obsC = Z_chaosC*cd_groundC - X_chaosC*sd_groundC #New C
    Y_obsC = Y_chaosC #New E
    
    SwarmDataC = pd.DataFrame({'F_res':Fc_res,'Nc':X_obsC,'Ec':Y_obsC, 'Cc':Z_obsC, 'Tc':X_obsC['Timestamp'], 'LatC':dsC['Latitude'], 'LongC':dsC['Longitude']})
    SwarmDataC['epoch'] = SwarmDataC['Tc'].astype('int64')//1e9
    SwarmDataC['epoch'] = SwarmDataC['epoch'].astype(int)
    SwarmDataC.set_index("epoch", inplace=True)
    ### End of Sat C request and process#####
    
    return SwarmDataA,SwarmDataB,SwarmDataC