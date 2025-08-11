"""
Module for fetching geomagnetic indices from HAPI servers.

This module provides functions to fetch AE (Auroral Electrojet) and SME (SuperMAG Electrojet) 
indices from their respective HAPI servers for validation and analysis of geomagnetic data.
"""

import pandas as pd
import numpy as np
from hapiclient import hapi
from hapiclient import hapitime2datetime


def get_ae_index(unique_dates, verbose=False):
    """
    Fetch AE, AL, and AU indices from NASA CDAWeb HAPI server.
    
    Parameters:
    -----------
    unique_dates : array-like
        Array of unique date strings in format 'YYYY-MM-DD'
    verbose : bool, optional
        If True, print progress information. Default is True.
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with DateTime index and columns ['AE_INDEX', 'AL_INDEX', 'AU_INDEX']
        Returns None if no data was fetched successfully.
    
    Example:
    --------
    >>> dates = ['2014-08-09']
    >>> ae_data = get_ae_index(dates)
    >>> print(ae_data.head())
    """
    server = 'https://cdaweb.gsfc.nasa.gov/hapi'
    dataset = 'OMNI_HRO_1MIN'
    parameters = 'AE_INDEX,AL_INDEX,AU_INDEX'
    
    if verbose:
        print(f"Fetching AE index data for {len(unique_dates)} unique dates...")
    
    all_data = []
    for date in unique_dates:
        start = f"{date}T00:00:00Z"
        stop = f"{date}T23:59:59Z"
        
        try:
            if verbose:
                print(f"Fetching data for {date}...")
            
            d, m = hapi(server, dataset, parameters, start, stop)
            
            # HAPI returns structured data - extract fields properly
            times = hapitime2datetime(d['Time'])
            
            # Create DataFrame with proper structure
            df = pd.DataFrame({
                'DateTime': times,
                'AE_INDEX': d['AE_INDEX'],
                'AL_INDEX': d['AL_INDEX'],
                'AU_INDEX': d['AU_INDEX'],
            })
            
            df.set_index('DateTime', inplace=True)
            all_data.append(df)
            
        except Exception as e:
            if verbose:
                print(f"Error fetching data for {date}: {e}")
            continue
    
    if all_data:
        df_ae_all = pd.concat(all_data)
        if verbose:
            print(f"Successfully fetched {len(df_ae_all)} AE index records")
            print("\nSample of fetched data:")
            print(df_ae_all.head())
            
            # Show data info
            print(f"\nData covers from {df_ae_all.index.min()} to {df_ae_all.index.max()}")
            print(f"Columns available: {list(df_ae_all.columns)}")
            
            # Show some statistics
            print(f"\nAE Index statistics:")
            print(f"Mean: {df_ae_all['AE_INDEX'].mean():.1f}")
        
        return df_ae_all
    else:
        if verbose:
            print("No AE data was fetched successfully")
        return None


def get_sme_index(unique_dates, verbose=True):
    """
    Fetch SME (SuperMAG Electrojet) index from SuperMAG HAPI server.
    
    Parameters:
    -----------
    unique_dates : array-like
        Array of unique date strings in format 'YYYY-MM-DD'
    verbose : bool, optional
        If True, print progress information. Default is True.
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with DateTime index and column ['SME']
        Returns None if no data was fetched successfully.
    
    Example:
    --------
    >>> dates = ['2014-08-09']
    >>> sme_data = get_sme_index(dates)
    >>> print(sme_data.head())
    """
    server_sme = 'https://supermag.jhuapl.edu/hapi'
    dataset_sme = 'indices_all'
    parameters_sme = 'SME'
    
    if verbose:
        print(f"Fetching SME index data for {len(unique_dates)} unique dates...")
    
    all_data = []
    for date in unique_dates:
        start = f"{date}T00:00:00Z"
        stop = f"{date}T23:59:59Z"
        
        try:
            if verbose:
                print(f"Fetching data for {date}...")
            
            d_2, m_2 = hapi(server_sme, dataset_sme, parameters_sme, start, stop)
            
            # HAPI returns structured data - extract fields properly
            times_2 = hapitime2datetime(d_2['Time'])
            
            # Create DataFrame with proper structure
            df = pd.DataFrame({
                'DateTime': times_2,
                'SME': d_2['SME']
            })
            
            df.set_index('DateTime', inplace=True)
            all_data.append(df)
            
        except Exception as e:
            if verbose:
                print(f"Error fetching data for {date}: {e}")
            continue
    
    if all_data:
        df_sme_all = pd.concat(all_data)
        if verbose:
            print(f"Successfully fetched {len(df_sme_all)} SME index records")
            print("\nSample of fetched data:")
            print(df_sme_all.head())
            
            # Show data info
            print(f"\nData covers from {df_sme_all.index.min()} to {df_sme_all.index.max()}")
            print(f"Columns available: {list(df_sme_all.columns)}")
            
            # Show some statistics
            print(f"\nSME Index statistics:")
            print(f"Mean: {df_sme_all['SME'].mean():.1f}")
        
        return df_sme_all
    else:
        if verbose:
            print("No SME data was fetched successfully")
        return None


def merge_indices_with_maggeo(df_csv, ae_data=None, sme_data=None, timestamp_col='timestamp'):
    """
    Merge AE and/or SME index data with MagGeo results.
    
    Parameters:
    -----------
    df_csv : pd.DataFrame
        Original MagGeo results DataFrame
    ae_data : pd.DataFrame, optional
        AE index data from get_ae_index()
    sme_data : pd.DataFrame, optional
        SME index data from get_sme_index()
    timestamp_col : str, optional
        Name of the timestamp column in df_csv. Default is 'timestamp'.
    
    Returns:
    --------
    pd.DataFrame
        Merged DataFrame with original MagGeo data and index data
    """
    # Ensure df_csv timestamp is timezone-aware to match the index data
    df_csv = df_csv.copy()  # Don't modify the original
    df_csv['timestamp_tz'] = pd.to_datetime(df_csv[timestamp_col]).dt.tz_localize('UTC')
    
    # Create a temporary dataframe for merging
    merge_df = df_csv.set_index('timestamp_tz')
    
    # Merge with AE data if provided
    if ae_data is not None:
        merge_df = merge_df.join(ae_data, how='left')
        print(f"Merged AE data - Points with AE data: {merge_df['AE_INDEX'].notna().sum()}")
    
    # Merge with SME data if provided
    if sme_data is not None:
        merge_df = merge_df.join(sme_data, how='left')
        print(f"Merged SME data - Points with SME data: {merge_df['SME'].notna().sum()}")
    
    # Clean up temporary columns
    if 'date' in merge_df.columns:
        merge_df.drop(columns=['date'], inplace=True)
    
    return merge_df
