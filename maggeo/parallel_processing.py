"""
Parallel processing utilities for MagGeo interpolation and CHAOS calculations.

This module provides functions to parallelize the MagGeo pipeline correctly:
- Only GPS trajectory data is chunked for parallel processing
- Complete Swarm data (A, B, C) is passed to each worker process
- Each GPS point can find its matches across all Swarm data for proper interpolation
- CHAOS calculations are performed after interpolation with correct data flow
"""

import multiprocessing as mp
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from functools import partial
import os
from tqdm import tqdm
from .interpolation import st_idw_process
from .chaos import chaos_ground_values


def get_optimal_chunk_size(total_gps_points: int, n_cores: int, min_chunk_size: int = 50) -> int:
    """
    Calculate optimal chunk size for GPS trajectory parallel processing.
    
    Parameters
    ----------
    total_gps_points : int
        Total number of GPS points in the trajectory
    n_cores : int
        Number of CPU cores available
    min_chunk_size : int, default 50
        Minimum chunk size to ensure efficiency
        
    Returns
    -------
    int
        Optimal chunk size for GPS trajectory chunking
    """
    # Create chunks that will keep workers busy but not too small to cause overhead
    chunk_size = max(total_gps_points // (n_cores * 4), min_chunk_size)
    return min(chunk_size, 200)  # Cap at 200 to avoid memory issues


def split_gps_trajectory_into_chunks(gps_df: pd.DataFrame, chunk_size: int) -> List[pd.DataFrame]:
    """
    Split GPS trajectory DataFrame into chunks for parallel processing.
    
    IMPORTANT: Only the GPS trajectory is chunked. Swarm data must remain complete
    for each worker to find proper matches for interpolation.
    
    Parameters
    ----------
    gps_df : pd.DataFrame
        GPS trajectory DataFrame to split
    chunk_size : int
        Size of each GPS chunk
        
    Returns
    -------
    List[pd.DataFrame]
        List of GPS trajectory chunks
    """
    chunks = []
    for i in range(0, len(gps_df), chunk_size):
        chunk = gps_df.iloc[i:i + chunk_size].copy()
        chunks.append(chunk)
    return chunks


def process_gps_chunk_complete_pipeline(
    chunk_data: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, int]
) -> pd.DataFrame:
    """
    Process a GPS trajectory chunk through the complete MagGeo pipeline.
    
    This function follows the correct MagGeo logic:
    1. For each GPS point in the chunk, interpolate using ALL Swarm data
    2. Calculate CHAOS ground values for all interpolated points
    3. Calculate additional geomagnetic components
    
    Parameters
    ----------
    chunk_data : tuple
        Tuple containing (gps_chunk, complete_swarm_a, complete_swarm_b, complete_swarm_c, dt_seconds)
        
    Returns
    -------
    pd.DataFrame
        Complete annotated DataFrame chunk with all geomagnetic values
    """
    gps_chunk, swarm_a_complete, swarm_b_complete, swarm_c_complete, dt_seconds = chunk_data
    
    # Step 1: Interpolation phase - process each GPS point with access to ALL Swarm data
    interpolation_results = []
    for _, gps_row in gps_chunk.iterrows():
        try:
            # Use the complete Swarm datasets for proper spatiotemporal matching
            interpolation_result = st_idw_process(
                gps_row['gpsLat'], gps_row['gpsLong'], gps_row['gpsAltitude'],
                gps_row['gpsDateTime'], gps_row['epoch'],
                swarm_a_complete, swarm_b_complete, swarm_c_complete, dt_seconds
            )
            interpolation_results.append(interpolation_result)
        except Exception as e:
            # Bad Point could be not points in Swarm data or other issues.
            bad_point_result = {
                'Latitude': gps_row['gpsLat'],
                'Longitude': gps_row['gpsLong'],
                'Altitude': gps_row['gpsAltitude'],
                'DateTime': gps_row['gpsDateTime'],
                'N_res': float('nan'),
                'E_res': float('nan'),
                'C_res': float('nan'),
                'TotalPoints': 0,
                'Minimum_Distance': float('nan'),
                'Average_Distance': float('nan'),
                'Kp': float('nan')
            }
            interpolation_results.append(bad_point_result)
    
    # Convert interpolation results to DataFrame
    gps_with_residuals = pd.DataFrame(interpolation_results)
    
    # Step 2: CHAOS calculations phase - only after interpolation is complete
    try:
        # Calculate CHAOS ground values for the entire chunk
        X_obs, Y_obs, Z_obs, X_obs_internal, Y_obs_internal, Z_obs_internal = chaos_ground_values(gps_with_residuals)
        
        # Add CHAOS results to the DataFrame
        gps_with_residuals['N'] = X_obs
        gps_with_residuals['E'] = Y_obs
        gps_with_residuals['C'] = Z_obs
        gps_with_residuals['N_Obs'] = X_obs_internal
        gps_with_residuals['E_Obs'] = Y_obs_internal
        gps_with_residuals['C_Obs'] = Z_obs_internal
        
        # Step 3: Calculate additional geomagnetic components
        gps_with_residuals['H'] = np.sqrt((gps_with_residuals['N']**2 + gps_with_residuals['E']**2))
        gps_with_residuals['D'] = np.degrees(np.arctan2(gps_with_residuals['E'], gps_with_residuals['N']))
        gps_with_residuals['I'] = np.degrees(np.arctan2(gps_with_residuals['C'], gps_with_residuals['H']))
        gps_with_residuals['F'] = np.sqrt((gps_with_residuals['N']**2 + gps_with_residuals['E']**2 + gps_with_residuals['C']**2))
        
    except Exception as e:
        # If CHAOS calculation fails, add NaN columns, this need to be handled gracefully
        for col in ['N', 'E', 'C', 'N_Obs', 'E_Obs', 'C_Obs', 'H', 'D', 'I', 'F']:
            gps_with_residuals[col] = float('nan')
    
    return gps_with_residuals


def parallel_maggeo_annotation(
    gps_df: pd.DataFrame,
    swarm_a: pd.DataFrame,
    swarm_b: pd.DataFrame,
    swarm_c: pd.DataFrame,
    dt_seconds: int = 14400,
    n_cores: Optional[int] = None,
    chunk_size: Optional[int] = None
) -> pd.DataFrame:
    
    """
    Perform parallel MagGeo annotation following the correct logic.
   
    - Only GPS trajectory is chunked for parallel processing
    - Complete Swarm data (A, B, C) is passed to each core
    - Each GPS point finds matches across ALL Swarm data for proper interpolation.
    - this could be enhaced with a better approach in the future.
    - CHAOS calculations follow after interpolation with correct data flow
    
    Parameters
    ----------
    gps_df : pd.DataFrame
        GPS trajectory DataFrame
    swarm_a, swarm_b, swarm_c : pd.DataFrame
        Complete Swarm satellite data DataFrames (NOT chunked)
    dt_seconds : int, default 14400
        Time window in seconds for interpolation
    n_cores : int, optional
        Number of cores to use. If None, uses all available cores.
    chunk_size : int, optional
        Size of GPS chunks for processing. If None, calculated automatically.
        
    Returns
    -------
    pd.DataFrame
        Complete annotated DataFrame with all geomagnetic values
    """
    #TODO: Adjust this to use when parallel is active and validate why it runs twice
    #print(f"🚀 Starting parallel MagGeo annotation:")
    #print(f"   📍 GPS points: {len(gps_df)}")
    #print(f"   🛰️ Swarm A records: {len(swarm_a)}")
    #print(f"   🛰️ Swarm B records: {len(swarm_b)}")
    #print(f"   🛰️ Swarm C records: {len(swarm_c)}")
    #print(f"   🔧 Using {n_cores} cores with chunk size: {chunk_size}")

    if n_cores is None:
        n_cores = mp.cpu_count()
    
    if chunk_size is None:
        chunk_size = get_optimal_chunk_size(len(gps_df), n_cores)
    
    # Split ONLY the GPS trajectory into chunks (Swarm data remains complete)
    gps_chunks = split_gps_trajectory_into_chunks(gps_df, chunk_size)
    
    # Prepare data for multiprocessing - each worker gets complete Swarm data
    chunk_data_list = [
        (gps_chunk, swarm_a, swarm_b, swarm_c, dt_seconds) 
        for gps_chunk in gps_chunks
    ]
    
    #print(f"📦 Created {len(gps_chunks)} GPS chunks for parallel processing")
    
    # Process GPS chunks in parallel with complete pipeline
    with mp.Pool(processes=n_cores) as pool:
        results = list(tqdm(
            pool.imap(process_gps_chunk_complete_pipeline, chunk_data_list),
            total=len(chunk_data_list),
            desc="🧮 Processing GPS chunks (interpolation + CHAOS)",
            unit="chunk"
        ))
    
    # Concatenate all results
    final_df = pd.concat(results, ignore_index=True)
    
    # Clean up intermediate columns
    columns_to_drop = ['N_res', 'E_res', 'C_res']
    final_df.drop(columns=[col for col in columns_to_drop if col in final_df.columns], inplace=True)
    
    print(f"✅ Parallel annotation completed: {len(final_df)} points processed")
    return final_df