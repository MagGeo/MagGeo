"""
Swarm satellite data client for MagGeo
@author: Fernando Benitez-Paez
date: July, 2025
"""

import datetime as dt
from typing import Tuple
import pandas as pd
import logging
from viresclient import set_token, SwarmRequest
from .exceptions import SwarmDataError

logger = logging.getLogger(__name__)


class SwarmClient:
    """Client for fetching Swarm satellite magnetic field data"""
    
    def __init__(self, token: str):
        """
        Initialize Swarm client with VirES token
        
        Args:
            token: VirES API authentication token
        """
        self.token = token
        set_token(token=token)
        logger.info("Swarm client initialized with VirES token")
    
    def get_residuals(self, start_time: dt.datetime, end_time: dt.datetime) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Fetch magnetic field residuals from all Swarm satellites for a time period.
        
        Args:
            start_time: Start datetime for data retrieval
            end_time: End datetime for data retrieval
            
        Returns:
            Tuple of DataFrames (Swarm-A, Swarm-B, Swarm-C) with magnetic residuals
            
        Raises:
            SwarmDataError: If data retrieval fails
        """
        try:
            # Define the magnetic field measurements to retrieve
            measurements = [
                'B_NEC',  # Magnetic field in NEC coordinates
                'B_NEC_res_CHAOS-Core',  # Residuals after CHAOS core field removal
            ]
            
            # Additional parameters for quality filtering
            auxiliaries = [
                'QDLat', 'QDLon',  # Quasi-dipole coordinates
                'MLT',  # Magnetic local time
            ]
            
            swarm_data = {}
            
            for satellite in ['A', 'B', 'C']:
                logger.debug(f"Fetching Swarm-{satellite} data from {start_time} to {end_time}")
                
                try:
                    # Create request for specific satellite
                    request = SwarmRequest()
                    request.set_collection(f"SW_OPER_MAG{satellite}_LR_1B")
                    request.set_products(measurements=measurements, auxiliaries=auxiliaries)
                    request.set_range_filter("Flags_B", 0, 1)  # Quality filter
                    
                    # Fetch data
                    data = request.get_between(start_time, end_time)
                    
                    if data.as_dataframe().empty:
                        logger.warning(f"No Swarm-{satellite} data available for {start_time.date()}")
                        swarm_data[satellite] = pd.DataFrame()
                    else:
                        df = data.as_dataframe()
                        
                        # Process and clean the data
                        processed_df = self._process_swarm_data(df, satellite)
                        swarm_data[satellite] = processed_df
                        
                        logger.debug(f"Retrieved {len(processed_df)} Swarm-{satellite} data points")
                
                except Exception as e:
                    logger.error(f"Failed to fetch Swarm-{satellite} data: {str(e)}")
                    swarm_data[satellite] = pd.DataFrame()
            
            return swarm_data['A'], swarm_data['B'], swarm_data['C']
            
        except Exception as e:
            raise SwarmDataError(f"Failed to retrieve Swarm data: {str(e)}") from e
    
    def _process_swarm_data(self, raw_data: pd.DataFrame, satellite: str) -> pd.DataFrame:
        """
        Process raw Swarm data into standardized format.
        
        Args:
            raw_data: Raw data from VirES client
            satellite: Satellite identifier ('A', 'B', or 'C')
            
        Returns:
            Processed DataFrame with standardized columns
        """
        try:
            # Create processed dataframe with standardized column names
            processed = pd.DataFrame()
            
            # Copy timestamp and convert to datetime if needed
            processed['timestamp'] = pd.to_datetime(raw_data.index)
            processed['epoch'] = raw_data.index
            
            # Geographic coordinates
            processed['Latitude'] = raw_data['Latitude']
            processed['Longitude'] = raw_data['Longitude']
            processed['Radius'] = raw_data['Radius']
            
            # Magnetic field components (NEC coordinates)
            processed['B_N'] = raw_data['B_NEC'][:, 0]  # North component
            processed['B_E'] = raw_data['B_NEC'][:, 1]  # East component  
            processed['B_C'] = raw_data['B_NEC'][:, 2]  # Center (radial) component
            
            # Residual components after CHAOS core field removal
            processed['B_N_res'] = raw_data['B_NEC_res_CHAOS-Core'][:, 0]
            processed['B_E_res'] = raw_data['B_NEC_res_CHAOS-Core'][:, 1]
            processed['B_C_res'] = raw_data['B_NEC_res_CHAOS-Core'][:, 2]
            
            # Quasi-dipole coordinates
            processed['QDLat'] = raw_data['QDLat']
            processed['QDLon'] = raw_data['QDLon']
            processed['MLT'] = raw_data['MLT']
            
            # Add satellite identifier
            processed['Satellite'] = satellite
            
            # Sort by timestamp
            processed = processed.sort_values('timestamp').reset_index(drop=True)
            
            # Remove any rows with NaN in critical columns
            critical_columns = ['B_N_res', 'B_E_res', 'B_C_res', 'Latitude', 'Longitude']
            processed = processed.dropna(subset=critical_columns)
            
            logger.debug(f"Processed {len(processed)} valid Swarm-{satellite} data points")
            
            return processed
            
        except Exception as e:
            raise SwarmDataError(f"Failed to process Swarm-{satellite} data: {str(e)}") from e
    
    def validate_token(self) -> bool:
        """
        Validate that the VirES token is working by making a test request.
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Make a minimal test request
            test_start = dt.datetime.now() - dt.timedelta(days=30)
            test_end = test_start + dt.timedelta(hours=1)
            
            request = SwarmRequest()
            request.set_collection("SW_OPER_MAGA_LR_1B")
            request.set_products(measurements=['B_NEC'])
            
            # Try to fetch just a small amount of data
            data = request.get_between(test_start, test_end, asynchronous=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return False