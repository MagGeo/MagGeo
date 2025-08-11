from typing import Dict, Any
import pandas as pd
import numpy as np
from .gps import get_gps_data
from .swarm import get_swarm_residuals
from .swarm_data_manager import SwarmDataManager
from .interpolation import st_idw_process
from .chaos import chaos_ground_values
from .parallel_processing import parallel_maggeo_annotation
from .debug import get_debugger
from .date_utils import identify_unique_dates
import datetime as dt
from tqdm import tqdm

def annotate_gps_with_geomag(
        params: Dict[str, Any], 
        use_swarm_manager: bool = False, 
        use_parallel: bool = False, 
        n_cores: int = None
        ) -> pd.DataFrame:
    """
    MagGeo annotation Pipeline.
    
    Parameters
    ----------
    params : dict 
        Dictionary with keys for GPS file, columns, and token.
    use_swarm_manager : bool, default False
        Whether to use the SwarmDataManager for more efficient data handling.
        If True, data will be saved locally and can be reused later.
    use_parallel : bool, default False
        Whether to use parallel processing for interpolation and CHAOS calculations.
        Significantly speeds up processing for large datasets.
    n_cores : int, optional
        Number of cores to use for parallel processing. If None, uses all available cores.
        
    Returns
    -------
    pd.DataFrame
        Annotated DataFrame with geomagnetic data.
    """

    # Initialize debugger
    debugger = get_debugger()
    debugger.log_parameters(params)

    # 0. Get the GPS track in a CSV format.
    # Input: csv file store in the data folder, validate if there is a altitude attribute.
    # Output: GPS Data as pandas DF.

    gps_df = get_gps_data(
        data_dir=params['data_dir'],
        gpsfilename=params['gpsfilename'],
        lat_col=params['lat_col'],
        lon_col=params['long_col'],
        datetime_col=params['datetime_col'],
        altitude_col=params.get('altitude_col', None)
    )
    
    debugger.print_dataframe_info(gps_df, "GPS")
    debugger.save_dataframe(gps_df, "gps_loaded.csv", "Loaded GPS data")

    # 2. Identify unique dates for Swarm data download process (including buffer dates)
    unique_dates_df = identify_unique_dates(gps_df) 
    unique_dates = unique_dates_df['date']  # Extract dates

    # 3. Download Swarm data for each date
    # For each day in the trajectory, Get the Swarm Data and Residuals: Get_Swarm_and_residuals
    # Input:  Date and Time variables
    # Output: Swarm DF for each Sat, including the residuals, and Quality Flags.
    
    if use_swarm_manager:
        # Use the SwarmDataManager for more efficient data handling
        debugger.log("Using SwarmDataManager for Swarm data download")
        swarm_manager = SwarmDataManager(
            data_dir=params.get('swarm_data_dir', 'temp_data/swarm_data'),
            file_format=params.get('swarm_file_format', 'parquet'),
            token=params.get('token')
        )
        swarm_a, swarm_b, swarm_c = swarm_manager.download_for_trajectory(
            gps_df, 
            resume=params.get('resume_swarm_download', True)
        )
    else:
        # Use the original method released in the first version of MagGeo. Ill keep it like this, so in case I need to change the logic, 
        # I can do it without affecting the SwarmDataManager.
        # But if works I will remove it in the next version, and process everything through the SwarmDataManager.

        swarm_a_list, swarm_b_list, swarm_c_list = [], [], []
        hours_added = dt.timedelta(hours = 23, minutes=59, seconds=59)  # Add 23 hours and 59 minutes to cover the full day of data

        for d in tqdm (unique_dates, desc="Getting Swarm Data"):

            debugger.log(f"Requesting data for date: {d}")
            startdate = dt.datetime.combine(d, dt.datetime.min.time())
            enddate = startdate + hours_added
            debugger.log_date_range(d, startdate, enddate)
            
            # Get Swarm data for the specified date range
            a, b, c = get_swarm_residuals(startdate, enddate, params.get('token'))
            
            debugger.log_swarm_data("A", d, a)
            debugger.log_swarm_data("B", d, b) 
            debugger.log_swarm_data("C", d, c)
            
            swarm_a_list.append(a)
            swarm_b_list.append(b)
            swarm_c_list.append(c)
            
        swarm_a = pd.concat(swarm_a_list)
        debugger.log_swarm_concat("A", swarm_a)
        
        swarm_b = pd.concat(swarm_b_list)
        debugger.log_swarm_concat("B", swarm_b)
        
        swarm_c = pd.concat(swarm_c_list)
        debugger.log_swarm_concat("C", swarm_c)


    # 4. Annotate with GeoMagnetic components each GPS point
    if use_parallel:
        # Use parallel processing for faster computation
        debugger.log("Using parallel processing")
        
        # Use the corrected parallel pipeline that follows MagGeo logic
        annotated_df = parallel_maggeo_annotation(
            gps_df, swarm_a, swarm_b, swarm_c,
            dt_seconds=params.get('dt_seconds', 14400),
            n_cores=n_cores,
            chunk_size=params.get('chunk_size', None)
        )
        
        debugger.log_interpolation_result(annotated_df)
        debugger.log_chaos_result(annotated_df)
        
    else:
        # This is the original sequential processing logic, The idea behind is to process each GPS point with the complete Swarm data
        # based on a sequential IDW interpolation process., for short routes it migth me more easy to understand and debug.
        # it also do not save any Swarm data, so does not require the SwarmDataManager, but is not as efficient as the parallel processing
        
        results = []
        for _, row in tqdm (gps_df.iterrows(), total=gps_df.shape[0], desc="Annotating your GPS Trajectory"):
            try:
                result = st_idw_process(
                    row['gpsLat'], row['gpsLong'], row['gpsAltitude'],
                    row['gpsDateTime'], row['epoch'],
                    swarm_a, swarm_b, swarm_c
                )
            except:
                print("Ups!.That was a bad Swarm Point, let's keep working with the next point")
                result = {
                    'Latitude': row['gpsLat'],
                    'Longitude': row['gpsLong'],
                    'Altitude': row['gpsAltitude'],
                    'DateTime': row['gpsDateTime'],
                    'N_res': float('nan'),
                    'E_res': float('nan'),
                    'C_res': float('nan'),
                    'TotalPoints': 0,
                    'Minimum_Distance': float('nan'),
                    'Average_Distance': float('nan'),
                    'Kp': float('nan')
                }
            results.append(result)
        annotated_df = pd.DataFrame(results)
        debugger.log_interpolation_result(annotated_df)

        # 5. Compute CHAOS ground values
        debugger.log("Computing CHAOS ground values")

        X_obs, Y_obs, Z_obs, X_obs_internal, Y_obs_internal, Z_obs_internal = chaos_ground_values(annotated_df)
        annotated_df['N'] = X_obs
        debugger.log_chaos_values("N (X_obs)", X_obs)
        
        annotated_df['E'] = Y_obs
        debugger.log_chaos_values("E (Y_obs)", Y_obs)
        
        annotated_df['C'] = Z_obs
        debugger.log_chaos_values("C (Z_obs)", Z_obs)
        
        annotated_df['N_Obs'] = X_obs_internal
        debugger.log_chaos_values("N_Obs (X_obs_internal)", X_obs_internal)
        
        annotated_df['E_Obs'] = Y_obs_internal
        debugger.log_chaos_values("E_Obs (Y_obs_internal)", Y_obs_internal)
        
        annotated_df['C_Obs'] = Z_obs_internal
        debugger.log_chaos_values("C_Obs (Z_obs_internal)", Z_obs_internal)
        
        # 5b. Compute additional geomagnetic components like H, Declination, the intensity and inclination
        annotated_df['H'] = np.sqrt((annotated_df['N']**2 + annotated_df['E']**2))
        annotated_df['D'] = np.degrees(np.arctan2(annotated_df['E'], annotated_df['N']))
        annotated_df['I'] = np.degrees(np.arctan2(annotated_df['C'], annotated_df['H']))
        annotated_df['F'] = np.sqrt((annotated_df['N']**2 + annotated_df['E']**2 + annotated_df['C']**2))
        
        debugger.log_chaos_result(annotated_df)
    
    #Drop duplicated and unnecessary columns. 
    columns_to_drop = ['Latitude', 'Longitude', 'DateTime', 'Altitude', 'N_res', 'E_res', 'C_res']
    annotated_df.drop(columns=[col for col in columns_to_drop if col in annotated_df.columns], inplace=True)
    
    debugger.log("Merging GPS DataFrame with annotated DataFrame")

    # 6. Merge GPS and annotated DataFrames
    gps_df_original = get_gps_data (data_dir=params['data_dir'],
                                    gpsfilename=params['gpsfilename'],
                                    lat_col=params['lat_col'],
                                    lon_col=params['long_col'],
                                    datetime_col=params['datetime_col'],
                                    altitude_col=params.get('altitude_col', None),
                                    return_original_cols=True)
    
    debugger.print_dataframe_info(gps_df_original, "Original GPS")
    debugger.print_dataframe_info(annotated_df, "Annotated")

    # Merge the two DataFrames
    MagGeoResult = pd.concat([gps_df_original, annotated_df], axis=1)
    debugger.print_dataframe_info(MagGeoResult, "MagGeoResult")
    debugger.save_maggeo_results(MagGeoResult, "MagGeoResult.csv", "MagGeo Results")

    print("Congrats! MagGeo has processed your GPS trajectory.")
    return MagGeoResult
