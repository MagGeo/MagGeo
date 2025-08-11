"""
Swarm Data Manager for MagGeo

This module provides independent functionality for downloading, saving, and loading
Swarm satellite data. It can be used independently from the main MagGeo pipeline
for users who want to:
1. Download Swarm data from large trajectories and save locally
2. Process data in batches 
3. Reuse previously downloaded data
4. Run interpolation processes separately

Key features:
- Batch downloading with progress tracking
- Multiple save/load formats (CSV, Parquet*)
- Data validation and quality checks
- Resume capability for interrupted downloads
- Memory-efficient processing for large datasets
"""

import os
import datetime as dt
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
import pandas as pd
from tqdm import tqdm
import warnings

from .swarm import get_swarm_residuals
from .date_utils import identify_unique_dates
from .debug import get_debugger


class SwarmDataManager:
    """
    Manages Swarm satellite data download, storage, and retrieval operations.
    
    This class provides a high-level interface for working with Swarm data
    independently from the main MagGeo pipeline.
    """
    
    def __init__(self, 
                 data_dir: str = "swarm_data",
                 file_format: str = "csv",
                 chunk_size: int = 10,
                 token: Optional[str] = None):
        """
        Initialize SwarmDataManager.
        
        Parameters
        ----------
        data_dir : str, default "swarm_data"
            Directory to store downloaded Swarm data
        file_format : str, default "parquet" 
            File format for saving data. Options: "csv", "parquet"
        chunk_size : int, default 10
            Number of dates to process in each batch
        token : str, optional
            VirES token for authentication
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.file_format = file_format.lower()
        if self.file_format not in ["csv", "parquet"]:
            raise ValueError("file_format must be one of: csv, or parquet")
            
        self.chunk_size = chunk_size
        self.token = token
        self.debugger = get_debugger()
        
        # Create subdirectories for each satellite
        for sat in ['A', 'B', 'C']:
            (self.data_dir / f"swarm_{sat}").mkdir(exist_ok=True)
    
    def download_for_trajectory(self,
                              gps_df: pd.DataFrame,
                              save_individual_files: bool = True,
                              save_concatenated: bool = True,
                              resume: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Download Swarm data for an entire GPS trajectory.
        
        Parameters
        ----------
        gps_df : pd.DataFrame
            GPS trajectory data with datetime information
        save_individual_files : bool, default True
            Whether to save individual daily files
        save_concatenated : bool, default True
            Whether to save concatenated files for each satellite
        resume : bool, default True
            Whether to skip already downloaded files
            
        Returns
        -------
        tuple
            Tuple of concatenated DataFrames for satellites A, B, C
        """
        self.debugger.log("Starting Swarm data download for trajectory")
        
        # Identify unique dates
        unique_dates_df = identify_unique_dates(gps_df)
        unique_dates = unique_dates_df['date']
        
        self.debugger.log(f"Need to download data for {len(unique_dates)} unique dates")
        
        return self.download_for_dates(
            unique_dates,
            save_individual_files=save_individual_files,
            save_concatenated=save_concatenated,
            resume=resume
        )
    
    def download_for_dates(self,
                          dates: List[dt.date],
                          save_individual_files: bool = True,
                          save_concatenated: bool = True,
                          resume: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Download Swarm data for specific dates.
        
        Parameters
        ----------
        dates : List[dt.date]
            List of dates to download data for
        save_individual_files : bool, default True
            Whether to save individual daily files
        save_concatenated : bool, default True
            Whether to save concatenated files for each satellite
        resume : bool, default True
            Whether to skip already downloaded files
            
        Returns
        -------
        tuple
            Tuple of concatenated DataFrames for satellites A, B, C
        """
        swarm_a_list, swarm_b_list, swarm_c_list = [], [], []
        
        # Filter dates if resuming
        if resume:
            dates_to_process = self._filter_existing_dates(dates)
            if len(dates_to_process) < len(dates):
                self.debugger.log(f"Resuming: {len(dates) - len(dates_to_process)} dates already downloaded")
                print(f"📁 Found existing data for {len(dates) - len(dates_to_process)} dates")
        else:
            dates_to_process = dates
        
        if not dates_to_process:
            print("✅ All Swarm data already downloaded!")
            # Load existing data
            existing_data = self._load_existing_data(dates)
            if existing_data:
                swarm_a_concat = pd.concat(existing_data[0]) if existing_data[0] else pd.DataFrame()
                swarm_b_concat = pd.concat(existing_data[1]) if existing_data[1] else pd.DataFrame()
                swarm_c_concat = pd.concat(existing_data[2]) if existing_data[2] else pd.DataFrame()
                return swarm_a_concat, swarm_b_concat, swarm_c_concat
        
        # Download data for each date with unified progress bar
        hours_added = dt.timedelta(hours=23, minutes=59, seconds=59)
        
        print(f"🛰️ Downloading Swarm data for {len(dates_to_process)} dates...")
        pbar = tqdm(dates_to_process, 
                   desc="Swarm Data Progress", 
                   unit="day",
                   bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} days [{elapsed}<{remaining}]')
        
        for date in pbar:
            try:
                # Update progress bar description with current date
                pbar.set_description(f"Downloading {date.strftime('%Y-%m-%d')}")
                
                startdate = dt.datetime.combine(date, dt.datetime.min.time())
                enddate = startdate + hours_added
                
                self.debugger.log(f"Downloading data for {date}")
                
                # Download data
                swarm_a, swarm_b, swarm_c = get_swarm_residuals(
                    startdate, enddate, self.token
                )
                
                # Add date metadata
                for df, sat_name in [(swarm_a, 'A'), (swarm_b, 'B'), (swarm_c, 'C')]:
                    df['download_date'] = date
                    df['data_quality'] = self._assess_data_quality(df)
                
                # Save individual files if requested
                if save_individual_files:
                    self._save_daily_data(date, swarm_a, swarm_b, swarm_c)
                
                swarm_a_list.append(swarm_a)
                swarm_b_list.append(swarm_b)
                swarm_c_list.append(swarm_c)
                
                # Update progress bar with success
                pbar.set_postfix(status="✓", refresh=False)
                
            except Exception as e:
                self.debugger.log(f"Error downloading data for {date}: {str(e)}", "error")
                warnings.warn(f"Failed to download data for {date}: {str(e)}")
                # Update progress bar with error
                pbar.set_postfix(status="✗", refresh=False)
                continue
        
        pbar.close()
        print("🎯 Swarm data download completed!")
        
        # Load any existing data if resuming
        if resume:
            existing_data = self._load_existing_data(dates)
            if existing_data:
                swarm_a_list.extend(existing_data[0])
                swarm_b_list.extend(existing_data[1]) 
                swarm_c_list.extend(existing_data[2])
        
        # Concatenate all data
        swarm_a_concat = pd.concat(swarm_a_list) if swarm_a_list else pd.DataFrame()
        swarm_b_concat = pd.concat(swarm_b_list) if swarm_b_list else pd.DataFrame()
        swarm_c_concat = pd.concat(swarm_c_list) if swarm_c_list else pd.DataFrame()
        
        # Save concatenated files if requested
        if save_concatenated and not swarm_a_concat.empty:
            self._save_concatenated_data(swarm_a_concat, swarm_b_concat, swarm_c_concat)
        
        self.debugger.log("Swarm data download completed")
        return swarm_a_concat, swarm_b_concat, swarm_c_concat
    
    def load_data_for_dates(self, 
                           dates: List[dt.date],
                           satellites: List[str] = ['A', 'B', 'C']) -> Dict[str, pd.DataFrame]:
        """
        Load previously downloaded Swarm data for specific dates.
        
        Parameters
        ----------
        dates : List[dt.date]
            List of dates to load data for
        satellites : List[str], default ['A', 'B', 'C']
            Which satellites to load data for
            
        Returns
        -------
        dict
            Dictionary with satellite names as keys and concatenated DataFrames as values
        """
        result = {}
        
        for sat in satellites:
            sat_data = []
            for date in dates:
                try:
                    daily_data = self._load_daily_data(date, sat)
                    if daily_data is not None:
                        sat_data.append(daily_data)
                except Exception as e:
                    self.debugger.log(f"Could not load data for {sat} on {date}: {str(e)}", "warning")
            
            if sat_data:
                result[sat] = pd.concat(sat_data)
            else:
                result[sat] = pd.DataFrame()
                
        return result
    
    def load_concatenated_data(self, 
                             satellites: List[str] = ['A', 'B', 'C']) -> Dict[str, pd.DataFrame]:
        """
        Load previously saved concatenated Swarm data.
        
        Parameters
        ---------- 
        satellites : List[str], default ['A', 'B', 'C']
            Which satellites to load data for
            
        Returns
        -------
        dict
            Dictionary with satellite names as keys and DataFrames as values
        """
        result = {}
        
        for sat in satellites:
            try:
                filepath = self.data_dir / f"swarm_{sat}_concatenated.{self.file_format}"
                
                if filepath.exists():
                    result[sat] = self._load_file(filepath)
                    self.debugger.log(f"Loaded concatenated data for satellite {sat}: {result[sat].shape}")
                else:
                    self.debugger.log(f"No concatenated data found for satellite {sat}", "warning")
                    result[sat] = pd.DataFrame()
                    
            except Exception as e:
                self.debugger.log(f"Error loading concatenated data for satellite {sat}: {str(e)}", "error")
                result[sat] = pd.DataFrame()
                
        return result
    
    def get_data_summary(self) -> pd.DataFrame:
        """
        Get summary of available downloaded data.
        
        Returns
        -------
        pd.DataFrame
            Summary of available data files with metadata
        """
        summary_data = []
        
        for sat in ['A', 'B', 'C']:
            sat_dir = self.data_dir / f"swarm_{sat}"
            
            if sat_dir.exists():
                for file_path in sat_dir.glob(f"*.{self.file_format}"):
                    # Extract date from filename
                    date_str = file_path.stem.replace(f"swarm_{sat}_", "")
                    
                    try:
                        file_date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
                        file_size = file_path.stat().st_size
                        
                        # Load file to get row count
                        df = self._load_file(file_path)
                        
                        summary_data.append({
                            'satellite': sat,
                            'date': file_date,
                            'filename': file_path.name,
                            'file_size_mb': round(file_size / (1024 * 1024), 2),
                            'row_count': len(df),
                            'data_quality': df['data_quality'].iloc[0] if 'data_quality' in df.columns else 'unknown'
                        })
                        
                    except Exception as e:
                        self.debugger.log(f"Error processing file {file_path}: {str(e)}", "warning")
        
        return pd.DataFrame(summary_data)
    
    def cleanup_data(self, 
                    older_than_days: Optional[int] = None,
                    quality_threshold: str = 'poor') -> int:
        """
        Clean up downloaded data files.
        
        Parameters
        ----------
        older_than_days : int, optional
            Remove files older than this many days
        quality_threshold : str, default 'poor'
            Remove files with data quality below this threshold
            
        Returns
        -------
        int
            Number of files removed
        """
        files_removed = 0
        
        for sat in ['A', 'B', 'C']:
            sat_dir = self.data_dir / f"swarm_{sat}"
            
            if sat_dir.exists():
                for file_path in sat_dir.glob(f"*.{self.file_format}"):
                    should_remove = False
                    
                    # Check age
                    if older_than_days:
                        file_age = dt.datetime.now() - dt.datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_age.days > older_than_days:
                            should_remove = True
                    
                    # Check quality
                    if quality_threshold and not should_remove:
                        try:
                            df = self._load_file(file_path)
                            if 'data_quality' in df.columns:
                                quality = df['data_quality'].iloc[0]
                                if quality == 'poor' and quality_threshold in ['good', 'fair']:
                                    should_remove = True
                                elif quality in ['poor', 'fair'] and quality_threshold == 'good':
                                    should_remove = True
                        except:
                            pass
                    
                    if should_remove:
                        file_path.unlink()
                        files_removed += 1
                        self.debugger.log(f"Removed file: {file_path}")
        
        return files_removed
    
    # Private methods
    def _filter_existing_dates(self, dates: List[dt.date]) -> List[dt.date]:
        """Filter out dates that already have downloaded data."""
        dates_to_process = []
        
        for date in dates:
            # Check if all satellites have data for this date
            all_exist = True
            for sat in ['A', 'B', 'C']:
                filepath = self.data_dir / f"swarm_{sat}" / f"swarm_{sat}_{date.strftime('%Y-%m-%d')}.{self.file_format}"
                if not filepath.exists():
                    all_exist = False
                    break
            
            if not all_exist:
                dates_to_process.append(date)
                
        return dates_to_process
    
    def _load_existing_data(self, dates: List[dt.date]) -> Optional[Tuple[List, List, List]]:
        """Load existing data for dates that have already been downloaded."""
        swarm_a_list, swarm_b_list, swarm_c_list = [], [], []
        
        for date in dates:
            try:
                # Check if data exists for all satellites
                data_exists = True
                for sat in ['A', 'B', 'C']:
                    filepath = self.data_dir / f"swarm_{sat}" / f"swarm_{sat}_{date.strftime('%Y-%m-%d')}.{self.file_format}"
                    if not filepath.exists():
                        data_exists = False
                        break
                
                if data_exists:
                    swarm_a = self._load_daily_data(date, 'A')
                    swarm_b = self._load_daily_data(date, 'B') 
                    swarm_c = self._load_daily_data(date, 'C')
                    
                    if swarm_a is not None and swarm_b is not None and swarm_c is not None:
                        swarm_a_list.append(swarm_a)
                        swarm_b_list.append(swarm_b)
                        swarm_c_list.append(swarm_c)
                        
            except Exception as e:
                self.debugger.log(f"Error loading existing data for {date}: {str(e)}", "warning")
        
        if swarm_a_list:
            return swarm_a_list, swarm_b_list, swarm_c_list
        return None
    
    def _save_daily_data(self, date: dt.date, swarm_a: pd.DataFrame, swarm_b: pd.DataFrame, swarm_c: pd.DataFrame):
        """Save daily data for each satellite."""
        date_str = date.strftime('%Y-%m-%d')
        
        for df, sat in [(swarm_a, 'A'), (swarm_b, 'B'), (swarm_c, 'C')]:
            filepath = self.data_dir / f"swarm_{sat}" / f"swarm_{sat}_{date_str}.{self.file_format}"
            self._save_file(df, filepath)
    
    def _load_daily_data(self, date: dt.date, satellite: str) -> Optional[pd.DataFrame]:
        """Load daily data for a specific satellite."""
        date_str = date.strftime('%Y-%m-%d')
        filepath = self.data_dir / f"swarm_{satellite}" / f"swarm_{satellite}_{date_str}.{self.file_format}"
        
        if filepath.exists():
            return self._load_file(filepath)
        return None
    
    def _save_concatenated_data(self, swarm_a: pd.DataFrame, swarm_b: pd.DataFrame, swarm_c: pd.DataFrame):
        """Save concatenated data for each satellite."""
        for df, sat in [(swarm_a, 'A'), (swarm_b, 'B'), (swarm_c, 'C')]:
            filepath = self.data_dir / f"swarm_{sat}_concatenated.{self.file_format}"
            self._save_file(df, filepath)
            self.debugger.log(f"Saved concatenated data for satellite {sat}: {filepath}")
    
    def _save_file(self, df: pd.DataFrame, filepath: Path):
        """Save DataFrame using the specified file format."""
        if self.file_format == "csv":
            df.to_csv(filepath, index=True)
        elif self.file_format == "parquet":
            df.to_parquet(filepath, index=True)
        #elif self.file_format == "pickle":
            #df.to_pickle(filepath)
    
    def _load_file(self, filepath: Path) -> pd.DataFrame:
        """Load DataFrame using the specified file format.""" 
        if self.file_format == "csv":
            return pd.read_csv(filepath, index_col=0)
        elif self.file_format == "parquet":
            return pd.read_parquet(filepath)
    
    def _assess_data_quality(self, df: pd.DataFrame) -> str:
        """Assess the quality of downloaded Swarm data."""
        if df.empty:
            return 'poor'
        
        # Check for missing values in key columns
        key_columns = ['N_res', 'E_res', 'C_res', 'F_res']
        missing_ratio = df[key_columns].isnull().sum().sum() / (len(df) * len(key_columns))
        
        if missing_ratio > 0.5:
            return 'poor'
        elif missing_ratio > 0.1:
            return 'fair'
        else:
            return 'good'


# Convenience functions for backward compatibility and ease of use
def download_swarm_data_for_trajectory(gps_df: pd.DataFrame,
                                      data_dir: str = "swarm_data",
                                      file_format: str = "csv",
                                      token: Optional[str] = None,
                                      resume: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Convenience function to download Swarm data for a GPS trajectory.
    
    Parameters
    ----------
    gps_df : pd.DataFrame
        GPS trajectory data
    data_dir : str, default "swarm_data"
        Directory to store data
    file_format : str, default "csv"
        File format for saving data
    token : str, optional
        VirES authentication token
    resume : bool, default True
        Whether to resume from existing downloads
        
    Returns
    -------
    tuple
        Tuple of concatenated DataFrames for satellites A, B, C
    """
    manager = SwarmDataManager(data_dir=data_dir, file_format=file_format, token=token)
    return manager.download_for_trajectory(gps_df, resume=resume)


def load_swarm_data(data_dir: str = "swarm_data",
                   file_format: str = "csv",
                   satellites: List[str] = ['A', 'B', 'C']) -> Dict[str, pd.DataFrame]:
    """
    Convenience function to load previously downloaded Swarm data.
    
    Parameters
    ----------
    data_dir : str, default "swarm_data"
        Directory containing the data
    file_format : str, default "csv"
        File format of the data
    satellites : List[str], default ['A', 'B', 'C']
        Which satellites to load
        
    Returns
    -------
    dict
        Dictionary with satellite names as keys and DataFrames as values
    """
    manager = SwarmDataManager(data_dir=data_dir, file_format=file_format)
    return manager.load_concatenated_data(satellites=satellites)
