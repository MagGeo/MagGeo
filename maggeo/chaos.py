
import pandas as pd
import numpy as np
from .auxiliaryfunctions import gg_to_geo
from typing import Dict, Any
from chaosmagpy import load_CHAOS_matfile, data_utils
import pooch

# 3. This function computes the CHAOS ground values based on the GPS trajectory and the Swarm residuals.
# This is key part of the MagGeo workflow, as it allows to compute the magnetic field components at ground level or 
# bird level, using the CHAOS model and the Swarm residuals.
# See the paper: Benitez-Paez, F., Brum-Bastos, V.d., Beggan, C.D. et al. Fusion of wildlife tracking and satellite geomagnetic data for the study of animal migration. Mov Ecol 9, 31 (2021). https://doi.org/10.1186/s40462-021-00268-4


def chaos_ground_values(GPS_ResInt):

    """Compute the CHAOS ground values based on GPS trajectory and Swarm residuals.
    This function loads the CHAOS model, computes the geocentric coordinates, and calculates the magnetic field components at ground level.
    It transforms the magnetic field components from geocentric to geodetic frame and returns the results.
    
    Parameters
    ----------
    utilities_dir : str
        Directory where the utilities are located, including the CHAOS model.
    GPS_ResInt : pd.DataFrame
        DataFrame containing the GPS trajectory and Swarm residuals.

    Returns
    -------
    tuple
        Tuple containing the computed magnetic field components in the geodetic frame:
        (X_obs, Y_obs, Z_obs, X_obs_internal, Y_obs_internal, Z_obs_internal).
    
    """

    chaos_matfile = pooch.retrieve(
    #"http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/CHAOS-7.15.mat",
    "http://www.spacecenter.dk/files/magnetic-models/CHAOS-8/_downloads/21c4a48c1467d2ad6f99621910f5399f/CHAOS-8.3.mat",
    known_hash="cd8b38fe88f6b75cfd3892ed224f125c1a73bd642ddd4f28e303345aa292e629",
    #progressbar=True,
    )

    # 1. Load the CHAOS model from the maggeo/models directory using a package-relative path
    #chaos_mat_path = importlib.resources.files('maggeo.models').joinpath('CHAOS-7.mat')
    # use chaos_mat_path (as a pathlib.Path object)
    model = load_CHAOS_matfile(str(chaos_matfile))
    theta = 90-GPS_ResInt['Latitude'].values
    phi = GPS_ResInt['Longitude'].values
    alt=GPS_ResInt['Altitude'].values
    rad_geoc_ground, theta_geoc_ground, sd_ground, cd_ground = gg_to_geo(alt, theta) 
    # gg_to_geo, will transform the coordinates from geocentric values to geodesic values. Altitude must be in km
    time = data_utils.mjd2000(
        pd.DatetimeIndex(GPS_ResInt['DateTime']).year,
        pd.DatetimeIndex(GPS_ResInt['DateTime']).month,
        pd.DatetimeIndex(GPS_ResInt['DateTime']).day
    )
    
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

    #6b. Rotate the X(N) and Z(C) magnetic field values of the internal part of chaos models into the geodetic frame using the sd and cd (sine and cosine d from gg_to_geo) 
    X_obs_internal = X_chaos_internal *cd_ground + Z_chaos_internal*sd_ground #New N
    Z_obs_internal = Z_chaos_internal *cd_ground - X_chaos_internal*sd_ground #New C
    Y_obs_internal = Y_chaos_internal # New E

    return X_obs, Y_obs, Z_obs, X_obs_internal, Y_obs_internal, Z_obs_internal



    """
    Process a single chunk of GPS data for CHAOS calculations.
    
    This is a helper function for parallel processing.
    
    Parameters
    ----------
    gps_resint_chunk : pd.DataFrame
        Chunk of GPS data with interpolated residuals
        
    Returns
    -------
    pd.DataFrame
        DataFrame chunk with CHAOS calculations
    """
    # Calculate CHAOS ground values for this chunk
    X_obs, Y_obs, Z_obs, X_obs_internal, Y_obs_internal, Z_obs_internal = chaos_ground_values(gps_resint_chunk)
    
    # Create a copy of the chunk and add CHAOS results
    result_chunk = gps_resint_chunk.copy()
    result_chunk['N'] = X_obs
    result_chunk['E'] = Y_obs
    result_chunk['C'] = Z_obs
    result_chunk['N_Obs'] = X_obs_internal
    result_chunk['E_Obs'] = Y_obs_internal
    result_chunk['C_Obs'] = Z_obs_internal
    
    # Calculate additional geomagnetic components
    result_chunk['H'] = np.sqrt((result_chunk['N']**2 + result_chunk['E']**2))
    result_chunk['D'] = np.degrees(np.arctan2(result_chunk['E'], result_chunk['N']))
    result_chunk['I'] = np.degrees(np.arctan2(result_chunk['C'], result_chunk['H']))
    result_chunk['F'] = np.sqrt((result_chunk['N']**2 + result_chunk['E']**2 + result_chunk['C']**2))
    
    return result_chunk