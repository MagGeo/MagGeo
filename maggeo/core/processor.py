"""
MagGeo Core Processor - Refactored for Performance and Maintainability
@author: Fernando Benitez-Paez
date: July, 2025
"""

import datetime as dt
from datetime import timedelta
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from viresclient import set_token
from .exceptions import MagGeoError, SwarmDataError, ValidationError
from .swarm_client import SwarmClient
from .interpolation import MagneticFieldInterpolator
from .chaos_model import CHAOSModel
from ..utils.validation import validate_gps_data, validate_config
from ..utils.gps_utils import process_gps_dates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MagGeoConfig:
    """Configuration for MagGeo processing"""
    token: str
    gps_filename: Optional[str] = None
    lat_column: str = "Latitude"
    lon_column: str = "Longitude" 
    datetime_column: str = "DateTime"
    altitude_column: str = "Altitude"
    output_dir: Path = Path("results")
    temp_dir: Optional[Path] = None
    max_workers: int = 4
    chunk_size: int = 1000


class MagGeoProcessor:
    """
    Main processor for annotating GPS trajectories with geomagnetic field data
    from Swarm satellites and CHAOS model.
    """
    
    def __init__(self, config: MagGeoConfig):
        self.config = config
        self.swarm_client = SwarmClient(config.token)
        self.interpolator = MagneticFieldInterpolator()
        self.chaos_model = CHAOSModel()
        
        # Set up directories
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        if self.config.temp_dir:
            self.config.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def process_trajectory(self, gps_data: Union[pd.DataFrame, str, Path]) -> pd.DataFrame:
        """
        Main processing pipeline for GPS trajectory annotation.
        
        Args:
            gps_data: GPS trajectory data as DataFrame or path to CSV file
            
        Returns:
            Annotated GPS trajectory with magnetic field components
            
        Raises:
            MagGeoError: If processing fails
            ValidationError: If input data is invalid
        """
        try:
            # Load and validate GPS data
            if isinstance(gps_data, (str, Path)):
                gps_df = self._load_gps_data(gps_data)
            else:
                gps_df = gps_data.copy()
            
            logger.info(f"Processing {len(gps_df)} GPS points")
            
            # Validate GPS data
            validate_gps_data(gps_df, self.config)
            
            # Process dates for Swarm data fetching
            unique_dates = self._extract_unique_dates(gps_df)
            logger.info(f"Fetching Swarm data for {len(unique_dates)} unique dates")
            
            # Fetch Swarm data for all required dates
            swarm_data = self._fetch_swarm_data_parallel(unique_dates)
            
            # Interpolate magnetic field values
            magnetic_data = self._interpolate_magnetic_fields(gps_df, swarm_data)
            
            # Add CHAOS model ground values
            magnetic_data = self._add_chaos_ground_values(magnetic_data)
            
            # Calculate derived magnetic components
            result = self._calculate_magnetic_components(magnetic_data)
            
            logger.info("Processing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            raise MagGeoError(f"Failed to process GPS trajectory: {str(e)}") from e
    
    def _load_gps_data(self, filepath: Union[str, Path]) -> pd.DataFrame:
        """Load GPS data from CSV file with validation"""
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                raise FileNotFoundError(f"GPS file not found: {filepath}")
            
            gps_df = pd.read_csv(filepath)
            
            # Convert datetime column
            if self.config.datetime_column in gps_df.columns:
                gps_df[self.config.datetime_column] = pd.to_datetime(
                    gps_df[self.config.datetime_column]
                )
            
            return gps_df
            
        except Exception as e:
            raise ValidationError(f"Failed to load GPS data: {str(e)}") from e
    
    def _extract_unique_dates(self, gps_df: pd.DataFrame) -> List[dt.date]:
        """
        Extract unique dates from GPS data, accounting for boundary conditions.
        
        This handles the original logic where data from previous/next day 
        might be needed for points near midnight.
        """
        dates_needed = set()
        
        for _, row in gps_df.iterrows():
            gps_datetime = row[self.config.datetime_column]
            current_date = gps_datetime.date()
            current_time = gps_datetime.time()
            
            dates_needed.add(current_date)
            
            # Add previous day if before 04:00
            if current_time < dt.time(4, 0, 0):
                dates_needed.add(current_date - timedelta(days=1))
            
            # Add next day if after 20:00
            if current_time > dt.time(20, 0, 0):
                dates_needed.add(current_date + timedelta(days=1))
        
        return sorted(list(dates_needed))
    
    def _fetch_swarm_data_parallel(self, dates: List[dt.date]) -> Dict[str, pd.DataFrame]:
        """
        Fetch Swarm data for multiple dates in parallel for better performance.
        """
        swarm_data = {'A': [], 'B': [], 'C': []}
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all date fetching tasks
            future_to_date = {
                executor.submit(self._fetch_swarm_data_for_date, date): date 
                for date in dates
            }
            
            # Collect results as they complete
            with tqdm(total=len(dates), desc="Fetching Swarm Data") as pbar:
                for future in as_completed(future_to_date):
                    date = future_to_date[future]
                    try:
                        data_a, data_b, data_c = future.result()
                        swarm_data['A'].append(data_a)
                        swarm_data['B'].append(data_b)  
                        swarm_data['C'].append(data_c)
                    except Exception as e:
                        logger.warning(f"Failed to fetch Swarm data for {date}: {str(e)}")
                        # Continue with other dates
                    finally:
                        pbar.update(1)
        
        # Concatenate all data efficiently
        consolidated_data = {}
        for satellite in ['A', 'B', 'C']:
            if swarm_data[satellite]:
                consolidated_data[satellite] = pd.concat(
                    swarm_data[satellite], 
                    ignore_index=True
                ).sort_values('timestamp')
            else:
                logger.warning(f"No Swarm-{satellite} data available")
                consolidated_data[satellite] = pd.DataFrame()
        
        return consolidated_data
    
    def _fetch_swarm_data_for_date(self, date: dt.date) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Fetch Swarm residuals for a specific date"""
        start_datetime = dt.datetime.combine(date, dt.datetime.min.time())
        end_datetime = start_datetime + timedelta(hours=24)
        
        return self.swarm_client.get_residuals(start_datetime, end_datetime)
    
    def _interpolate_magnetic_fields(self, gps_df: pd.DataFrame, 
                                   swarm_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Interpolate magnetic field values for all GPS points using vectorized operations.
        """
        results = []
        
        # Process in chunks for memory efficiency
        chunk_size = self.config.chunk_size
        total_chunks = (len(gps_df) + chunk_size - 1) // chunk_size
        
        with tqdm(total=len(gps_df), desc="Interpolating Magnetic Fields") as pbar:
            for i in range(0, len(gps_df), chunk_size):
                chunk = gps_df.iloc[i:i + chunk_size]
                chunk_results = self._process_gps_chunk(chunk, swarm_data)
                results.extend(chunk_results)
                pbar.update(len(chunk))
        
        return pd.DataFrame(results)
    
    def _process_gps_chunk(self, gps_chunk: pd.DataFrame, 
                          swarm_data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Process a chunk of GPS points for interpolation"""
        chunk_results = []
        
        for _, row in gps_chunk.iterrows():
            gps_point = {
                'latitude': row[self.config.lat_column],
                'longitude': row[self.config.lon_column],
                'altitude': row[self.config.altitude_column],
                'datetime': row[self.config.datetime_column]
            }
            
            try:
                interpolated = self.interpolator.interpolate_point(gps_point, swarm_data)
                chunk_results.append(interpolated)
            except Exception as e:
                logger.warning(f"Interpolation failed for point {gps_point}: {str(e)}")
                # Add placeholder result for failed point
                chunk_results.append({
                    'Latitude': gps_point['latitude'],
                    'Longitude': gps_point['longitude'],
                    'Altitude': gps_point['altitude'],
                    'DateTime': gps_point['datetime'],
                    'N_res': np.nan,
                    'E_res': np.nan,
                    'C_res': np.nan,
                    'TotalPoints': 0,
                    'Minimum_Distance': np.nan,
                    'Average_Distance': np.nan
                })
        
        return chunk_results
    
    def _add_chaos_ground_values(self, magnetic_data: pd.DataFrame) -> pd.DataFrame:
        """Add CHAOS model ground values to the magnetic data"""
        try:
            # Get CHAOS ground values
            chaos_values = self.chaos_model.get_ground_values(magnetic_data)
            
            # Add to dataframe
            magnetic_data['N'] = chaos_values['N']
            magnetic_data['E'] = chaos_values['E'] 
            magnetic_data['C'] = chaos_values['C']
            magnetic_data['N_Obs'] = chaos_values['N_internal']
            magnetic_data['E_Obs'] = chaos_values['E_internal']
            magnetic_data['C_Obs'] = chaos_values['C_internal']
            
            # Remove residual columns as they're no longer needed
            magnetic_data.drop(columns=['N_res', 'E_res', 'C_res'], inplace=True, errors='ignore')
            
            return magnetic_data
            
        except Exception as e:
            raise MagGeoError(f"Failed to add CHAOS ground values: {str(e)}") from e
    
    def _calculate_magnetic_components(self, magnetic_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived magnetic field components (H, D, I, F) from N, E, C components.
        
        Uses vectorized operations for better performance.
        """
        # Horizontal intensity
        magnetic_data['H'] = np.sqrt(magnetic_data['N']**2 + magnetic_data['E']**2)
        
        # Declination (in degrees)
        magnetic_data['D'] = np.degrees(np.arctan2(magnetic_data['E'], magnetic_data['N']))
        
        # Inclination (in degrees)  
        magnetic_data['I'] = np.degrees(np.arctan2(magnetic_data['C'], magnetic_data['H']))
        
        # Total field intensity
        magnetic_data['F'] = np.sqrt(
            magnetic_data['N']**2 + 
            magnetic_data['E']**2 + 
            magnetic_data['C']**2
        )
        
        return magnetic_data
    
    def save_results(self, result_df: pd.DataFrame, 
                    original_gps_data: pd.DataFrame, 
                    output_filename: Optional[str] = None) -> Path:
        """
        Save the annotated results to a CSV file.
        
        Args:
            result_df: Processed magnetic field data
            original_gps_data: Original GPS trajectory data
            output_filename: Optional custom filename
            
        Returns:
            Path to the saved file
        """
        try:
            # Combine original GPS data with results
            final_result = pd.concat([original_gps_data, result_df], axis=1)
            
            # Remove duplicate columns
            final_result = final_result.loc[:, ~final_result.columns.duplicated()]
            
            # Generate output filename
            if output_filename is None:
                timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"MagGeoResult_{timestamp}.csv"
            
            output_path = self.config.output_dir / output_filename
            
            # Save to CSV
            final_result.to_csv(output_path, index=False)
            
            logger.info(f"Results saved to: {output_path}")
            return output_path
            
        except Exception as e:
            raise MagGeoError(f"Failed to save results: {str(e)}") from e


# Convenience function for simple usage
def process_gps_trajectory(gps_data: Union[pd.DataFrame, str, Path], 
                          token: str,
                          **kwargs) -> pd.DataFrame:
    """
    Convenience function to process a GPS trajectory with default settings.
    
    Args:
        gps_data: GPS trajectory data or path to CSV file
        token: VirES API token
        **kwargs: Additional configuration options
        
    Returns:
        Annotated GPS trajectory with magnetic field data
    """
    config = MagGeoConfig(token=token, **kwargs)
    processor = MagGeoProcessor(config)
    return processor.process_trajectory(gps_data)