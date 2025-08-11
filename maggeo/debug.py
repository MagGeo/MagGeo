"""
Debug utilities for MagGeo package.
"""
import os
import logging
import pandas as pd
from pathlib import Path
from typing import Any, Optional

class MagGeoDebugger:
    """Debug helper for MagGeo operations."""
    
    def __init__(self, debug_mode: Optional[bool] = None):
        # Check if debug mode is enabled via environment variable or parameter
        self.debug_mode = debug_mode if debug_mode is not None else os.getenv('MAGGEO_DEBUG', 'false').lower() == 'true'
        self.temp_dir = Path("temp_data")
        
        if self.debug_mode:
            self._setup_debug_environment()
    
    def _setup_debug_environment(self):
        """Setup debug environment: create temp directory and configure logging."""
        # Ensure temp_data directory exists
        self.temp_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),  # Console output
                logging.FileHandler(self.temp_dir / 'maggeo_debug.log')  # File output
            ]
        )
        self.logger = logging.getLogger('MagGeo')
        self.logger.info("Debug mode enabled")
    
    def log(self, message: str, level: str = 'info'):
        """Log a debug message if debug mode is enabled."""
        if self.debug_mode:
            getattr(self.logger, level.lower())(message)
    
    def save_dataframe(self, df: pd.DataFrame, filename: str, description: str = ""):
        """Save DataFrame to temp directory if debug mode is enabled."""
        if self.debug_mode:
            filepath = self.temp_dir / filename
            df.to_csv(filepath, index=False)
            self.log(f"Saved {description}: {filepath} (shape: {df.shape})")
    
    def print_dataframe_info(self, df: pd.DataFrame, name: str):
        """Print DataFrame info if debug mode is enabled."""
        if self.debug_mode:
            self.log(f"{name} DataFrame shape: {df.shape}")
            self.log(f"{name} head:\n{df.head()}")
    
    def log_parameters(self, params: dict):
        """Log parameters if debug mode is enabled."""
        if self.debug_mode:
            self.log(f"Parameters: {params}")
    
    def log_unique_dates(self, dates):
        """Log unique dates if debug mode is enabled."""
        if self.debug_mode:
            self.log(f"Unique dates: {list(dates)}")
    
    def log_date_range(self, date, start_date, end_date):
        """Log date range for Swarm data request."""
        if self.debug_mode:
            self.log(f"Requesting data for {date}: {start_date} to {end_date}")
    
    def log_swarm_data(self, satellite: str, date, df: pd.DataFrame):
        """Log Swarm data information."""
        if self.debug_mode:
            self.log(f"Swarm {satellite} DataFrame for {date}: shape {df.shape}")
            self.save_dataframe(df, f"swarm_{satellite}_{date}.csv", f"Swarm {satellite} data for {date}")
    
    def log_swarm_concat(self, satellite: str, df: pd.DataFrame):
        """Log concatenated Swarm data information."""
        if self.debug_mode:
            self.log(f"Swarm {satellite} Concat DataFrame: shape {df.shape}")
            self.save_dataframe(df, f"swarm_Concat_{satellite}.csv", f"Concatenated Swarm {satellite} data")
    
    def log_chaos_values(self, component: str, values):
        """Log CHAOS model values.""" 
        if self.debug_mode:
            self.log(f"{component} values: {values}")
    
    def log_interpolation_result(self, df: pd.DataFrame):
        """Log interpolation results."""
        if self.debug_mode:
            self.log(f"After interpolation, DataFrame shape: {df.shape}")
            self.save_dataframe(df, "interpolated.csv", "Interpolated data")
    
    def log_chaos_result(self, df: pd.DataFrame):
        """Log CHAOS model results."""
        if self.debug_mode:
            self.log(f"After CHAOS model, DataFrame shape: {df.shape}")
            self.save_dataframe(df, "chaos_annotated.csv", "CHAOS annotated data")

    def save_maggeo_results(self, df: pd.DataFrame, filename: str, description: str = ""):
            """Save MagGeo Results to temp directory if debug mode is enabled."""
            if self.debug_mode:
                filepath = self.temp_dir / filename
                df.to_csv(filepath, index=False)
                self.log(f"Saved {description}: {filepath} (shape: {df.shape})")


# Global debugger instance
_debugger = None

def get_debugger() -> MagGeoDebugger:
    """Get or create the global debugger instance."""
    global _debugger
    if _debugger is None:
        _debugger = MagGeoDebugger()
    return _debugger
