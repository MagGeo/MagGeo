"""
Date utilities for MagGeo trajectory processing.

This module contains functions for processing and analyzing dates in GPS trajectories,
particularly for determining the unique dates needed for Swarm satellite data download.

Main function:
- identify_unique_dates(): Analyzes GPS trajectories to determine unique dates needed for Swarm data download. 
Swarm satellite mission and its data are polar orbits and typically available in 1-day intervals (every second),
so this function identifies a buffer dates for early morning and late evening GPS points to ensure complete coverage that matches
the time window of 4 hours before and after the GPS point.

See the paper:
- Benitez, F., et al. (2021). Fusion of wildlife tracking and satellite geomagnetic data for the study of animal migration. 
https://doi.org/10.1186/s40462-021-00268-4
  
"""

from typing import Dict, Any
import pandas as pd
from .debug import get_debugger


def identify_unique_dates(gps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify unique dates for Swarm data download process.
    
    This function analyzes the GPS trajectory to determine all unique dates
    that need Swarm data. It includes buffer dates for early morning and
    late evening GPS points to ensure complete coverage.
    
    Args:
        gps_df (pd.DataFrame): GPS DataFrame with 'dates' and 'times' columns
        
    Returns:
        pd.DataFrame: DataFrame with unique dates and metadata for Swarm data download
                     Columns: ['date', 'is_buffer_date', 'buffer_type', 'original_date']
    """
    debugger = get_debugger()
    debugger.log("Starting unique dates identification process")
    
    # Create time string column for filtering
    gps_df['time_str'] = gps_df['times'].apply(lambda t: t.strftime('%H:%M:%S'))
    
    # Identify early morning and late evening points
    early_mask = gps_df['time_str'] < '04:00:00'
    late_mask = gps_df['time_str'] > '20:00:00'
    
    debugger.log(f"Found {early_mask.sum()} early morning points (before 04:00:00)")
    debugger.log(f"Found {late_mask.sum()} late evening points (after 20:00:00)")
    
    # Collect all dates needed
    dates_data = []
    
    # Add original dates
    for date in gps_df['dates'].unique():
        dates_data.append({
            'date': date,
            'is_buffer_date': False,
            'buffer_type': None,
            'original_date': date
        })
    
    # Add buffer dates for early morning points (previous day)
    for date in gps_df.loc[early_mask, 'dates'].unique():
        buffer_date = date - pd.Timedelta(days=1)
        dates_data.append({
            'date': buffer_date,
            'is_buffer_date': True,
            'buffer_type': 'early_morning',
            'original_date': date
        })
    
    # Add buffer dates for late evening points (next day)
    for date in gps_df.loc[late_mask, 'dates'].unique():
        buffer_date = date + pd.Timedelta(days=1)
        dates_data.append({
            'date': buffer_date,
            'is_buffer_date': True,
            'buffer_type': 'late_evening',
            'original_date': date
        })
    
    # Create DataFrame and remove duplicates
    unique_dates_df = pd.DataFrame(dates_data)
    unique_dates_df = unique_dates_df.drop_duplicates(subset=['date']).sort_values('date').reset_index(drop=True)
    
    debugger.log(f"Total unique dates identified: {len(unique_dates_df)}")
    debugger.log(f"Original trajectory dates: {len(gps_df['dates'].unique())}")
    debugger.log(f"Buffer dates added: {unique_dates_df['is_buffer_date'].sum()}")
    debugger.log_unique_dates(unique_dates_df['date'])
    
    # Clean up temporary column
    gps_df.drop(columns=['time_str'], inplace=True)
    
    return unique_dates_df
