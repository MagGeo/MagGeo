"""
Input validation utilities for MagGeo
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
import logging

from ..core.exceptions import ValidationError, ConfigurationError

logger = logging.getLogger(__name__)


def validate_gps_data(gps_data: pd.DataFrame, config) -> None:
    """
    Validate GPS trajectory data for required columns and value ranges.
    
    Args:
        gps_data: GPS trajectory DataFrame
        config: MagGeoConfig object with column specifications
        
    Raises:
        ValidationError: If validation fails
    """
    if gps_data.empty:
        raise ValidationError("GPS data is empty")
    
    # Check required columns exist
    required_columns = [
        config.lat_column,
        config.lon_column, 
        config.datetime_column,
        config.altitude_column
    ]
    
    missing_columns = []
    for col in required_columns:
        if col not in gps_data.columns:
            missing_columns.append(col)
    
    if missing_columns:
        raise ValidationError(f"Missing required columns: {missing_columns}")
    
    # Validate coordinate ranges
    lat_data = gps_data[config.lat_column]
    lon_data = gps_data[config.lon_column]
    alt_data = gps_data[config.altitude_column]
    
    # Check latitude range (-90 to 90)
    if (lat_data < -90).any() or (lat_data > 90).any():
        invalid_lats = lat_data[(lat_data < -90) | (lat_data > 90)]
        raise ValidationError(f"Invalid latitude values found: {invalid_lats.tolist()[:5]}...")
    
    # Check longitude range (-180 to 180)
    if (lon_data < -180).any() or (lon_data > 180).any():
        invalid_lons = lon_data[(lon_data < -180) | (lon_data > 180)]
        raise ValidationError(f"Invalid longitude values found: {invalid_lons.tolist()[:5]}...")
    
    # Check altitude is reasonable (allow some negative values for below sea level)
    if (alt_data < -500).any() or (alt_data > 100000).any():
        invalid_alts = alt_data[(alt_data < -500) | (alt_data > 100000)]
        logger.warning(f"Unusual altitude values found: {invalid_alts.tolist()[:5]}...")
    
    # Check for NaN values in critical columns
    for col in required_columns:
        nan_count = gps_data[col].isna().sum()
        if nan_count > 0:
            logger.warning(f"Found {nan_count} NaN values in column '{col}'")
            if nan_count == len(gps_data):
                raise ValidationError(f"All values in column '{col}' are NaN")
    
    # Validate datetime column
    try:
        datetime_col = pd.to_datetime(gps_data[config.datetime_column])
        
        # Check for reasonable date range (not too far in past/future)
        min_date = datetime_col.min()
        max_date = datetime_col.max()
        
        if min_date.year < 2000:
            logger.warning(f"GPS data contains dates before 2000: {min_date}")
        if max_date.year > 2030:
            logger.warning(f"GPS data contains dates after 2030: {max_date}")
            
        # Check temporal resolution
        time_diffs = datetime_col.diff().dropna()
        if len(time_diffs) > 0:
            median_interval = time_diffs.median()
            logger.info(f"Median GPS sampling interval: {median_interval}")
            
            # Warn if intervals are very irregular
            std_interval = time_diffs.std()
            if std_interval > median_interval:
                logger.warning("GPS data has irregular time intervals")
                
    except Exception as e:
        raise ValidationError(f"Invalid datetime format in column '{config.datetime_column}': {str(e)}")
    
    logger.info(f"GPS data validation passed: {len(gps_data)} points, "
                f"date range: {min_date.date()} to {max_date.date()}")


def validate_config(config_dict: Dict[str, Any]) -> None:
    """
    Validate MagGeo configuration parameters.
    
    Args:
        config_dict: Configuration dictionary
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    if 'maggeo' not in config_dict:
        raise ConfigurationError("Configuration must contain 'maggeo' section")
    
    maggeo_config = config_dict['maggeo']
    
    # Required configuration fields
    required_fields = ['Lat', 'Long', 'DateTime', 'altitude']
    
    for field in required_fields:
        if field not in maggeo_config:
            raise ConfigurationError(f"Missing required configuration field: {field}")
        
        if not isinstance(maggeo_config[field], str):
            raise ConfigurationError(f"Configuration field '{field}' must be a string")
    
    # Optional GPS filename validation
    if 'gpsfilename' in maggeo_config:
        gps_file = maggeo_config['gpsfilename']
        if not isinstance(gps_file, str):
            raise ConfigurationError("gpsfilename must be a string")
        
        # Check file extension
        if not gps_file.lower().endswith('.csv'):
            logger.warning(f"GPS filename '{gps_file}' doesn't have .csv extension")
    
    logger.info("Configuration validation passed")


def validate_swarm_data(swarm_data: Dict[str, pd.DataFrame]) -> None:
    """
    Validate Swarm satellite data structure and content.
    
    Args:
        swarm_data: Dictionary with Swarm A, B, C data
        
    Raises:
        ValidationError: If Swarm data is invalid
    """
    required_satellites = ['A', 'B', 'C']
    
    for sat in required_satellites:
        if sat not in swarm_data:
            raise ValidationError(f"Missing Swarm-{sat} data")
        
        sat_data = swarm_data[sat]
        
        if sat_data.empty:
            logger.warning(f"Swarm-{sat} data is empty")
            continue
        
        # Check required columns
        required_cols = ['timestamp', 'Latitude', 'Longitude', 'B_N_res', 'B_E_res', 'B_C_res']
        missing_cols = [col for col in required_cols if col not in sat_data.columns]
        
        if missing_cols:
            raise ValidationError(f"Swarm-{sat} missing columns: {missing_cols}")
        
        # Validate coordinate ranges
        if (sat_data['Latitude'] < -90).any() or (sat_data['Latitude'] > 90).any():
            raise ValidationError(f"Invalid Swarm-{sat} latitude values")
        
        if (sat_data['Longitude'] < -180).any() or (sat_data['Longitude'] > 180).any():
            raise ValidationError(f"Invalid Swarm-{sat} longitude values")
        
        # Check for reasonable magnetic field residual values (nT)
        for component in ['B_N_res', 'B_E_res', 'B_C_res']:
            values = sat_data[component]
            if values.abs().max() > 10000:  # 10,000 nT seems excessive for residuals
                logger.warning(f"Large Swarm-{sat} {component} residuals detected (max: {values.abs().max():.1f} nT)")
        
        # Check temporal ordering
        if not sat_data['timestamp'].is_monotonic_increasing:
            logger.warning(f"Swarm-{sat} timestamps are not monotonically increasing")
    
    logger.info(f"Swarm data validation passed: {sum(len(data) for data in swarm_data.values())} total points")


def validate_interpolation_result(result: Dict[str, Any]) -> None:
    """
    Validate interpolation result for a single GPS point.
    
    Args:
        result: Interpolation result dictionary
        
    Raises:
        ValidationError: If result is invalid
    """
    required_fields = [
        'Latitude', 'Longitude', 'Altitude', 'DateTime',
        'N_res', 'E_res', 'C_res', 'TotalPoints'
    ]
    
    for field in required_fields:
        if field not in result:
            raise ValidationError(f"Missing interpolation result field: {field}")
    
    # Check coordinate ranges
    if not -90 <= result['Latitude'] <= 90:
        raise ValidationError(f"Invalid interpolated latitude: {result['Latitude']}")
    
    if not -180 <= result['Longitude'] <= 180:
        raise ValidationError(f"Invalid interpolated longitude: {result['Longitude']}")
    
    # Check that we used some data points for interpolation
    if result['TotalPoints'] < 0:
        raise ValidationError(f"Invalid TotalPoints: {result['TotalPoints']}")
    
    # Warn if interpolation used very few points
    if result['TotalPoints'] < 3:
        logger.warning(f"Interpolation used only {result['TotalPoints']} data points")
    
    # Check for reasonable magnetic field residual values
    for component in ['N_res', 'E_res', 'C_res']:
        value = result[component]
        if not np.isnan(value) and abs(value) > 5000:  # 5000 nT threshold
            logger.warning(f"Large interpolated {component} residual: {value:.1f} nT")


def validate_magnetic_components(magnetic_data: pd.DataFrame) -> None:
    """
    Validate calculated magnetic field components.
    
    Args:
        magnetic_data: DataFrame with magnetic field components
        
    Raises:
        ValidationError: If magnetic components are invalid
    """
    required_components = ['N', 'E', 'C', 'H', 'D', 'I', 'F']
    
    missing_components = [comp for comp in required_components if comp not in magnetic_data.columns]
    if missing_components:
        raise ValidationError(f"Missing magnetic components: {missing_components}")
    
    # Physical consistency checks
    for idx, row in magnetic_data.iterrows():
        # Check H = sqrt(N² + E²)
        calculated_h = np.sqrt(row['N']**2 + row['E']**2)
        if not np.isnan(row['H']) and abs(row['H'] - calculated_h) > 1.0:  # 1 nT tolerance
            logger.warning(f"H component inconsistency at index {idx}: {row['H']:.1f} vs {calculated_h:.1f}")
        
        # Check F = sqrt(N² + E² + C²)
        calculated_f = np.sqrt(row['N']**2 + row['E']**2 + row['C']**2)
        if not np.isnan(row['F']) and abs(row['F'] - calculated_f) > 1.0:  # 1 nT tolerance
            logger.warning(f"F component inconsistency at index {idx}: {row['F']:.1f} vs {calculated_f:.1f}")
        
        # Check reasonable field strength (Earth's field is ~25,000-65,000 nT)
        if not np.isnan(row['F']) and not (15000 <= abs(row['F']) <= 70000):
            logger.warning(f"Unusual total field strength at index {idx}: {row['F']:.1f} nT")
        
        # Check declination range (-180 to 180 degrees)
        if not np.isnan(row['D']) and not (-180 <= row['D'] <= 180):
            logger.warning(f"Invalid declination at index {idx}: {row['D']:.1f}°")
        
        # Check inclination range (-90 to 90 degrees)
        if not np.isnan(row['I']) and not (-90 <= row['I'] <= 90):
            logger.warning(f"Invalid inclination at index {idx}: {row['I']:.1f}°")
    
    logger.info(f"Magnetic components validation passed for {len(magnetic_data)} points")


def check_data_coverage(gps_data: pd.DataFrame, swarm_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Check temporal and spatial coverage between GPS and Swarm data.
    
    Args:
        gps_data: GPS trajectory data
        swarm_data: Swarm satellite data
        
    Returns:
        Dictionary with coverage statistics
    """
    coverage_stats = {
        'gps_time_range': None,
        'swarm_time_range': {},
        'temporal_overlap': {},
        'spatial_overlap': {},
        'coverage_quality': 'unknown'
    }
    
    try:
        # GPS time range
        gps_start = gps_data['DateTime'].min() if 'DateTime' in gps_data.columns else None
        gps_end = gps_data['DateTime'].max() if 'DateTime' in gps_data.columns else None
        coverage_stats['gps_time_range'] = (gps_start, gps_end)
        
        # Swarm time ranges and overlaps
        total_overlap_hours = 0
        satellites_with_data = 0
        
        for sat in ['A', 'B', 'C']:
            if sat in swarm_data and not swarm_data[sat].empty:
                sat_data = swarm_data[sat]
                sat_start = sat_data['timestamp'].min()
                sat_end = sat_data['timestamp'].max()
                
                coverage_stats['swarm_time_range'][sat] = (sat_start, sat_end)
                
                # Calculate temporal overlap
                if gps_start and gps_end:
                    overlap_start = max(gps_start, sat_start)
                    overlap_end = min(gps_end, sat_end)
                    
                    if overlap_start < overlap_end:
                        overlap_hours = (overlap_end - overlap_start).total_seconds() / 3600
                        coverage_stats['temporal_overlap'][sat] = overlap_hours
                        total_overlap_hours += overlap_hours
                        satellites_with_data += 1
                    else:
                        coverage_stats['temporal_overlap'][sat] = 0
                
                # Spatial coverage check (rough)
                if 'Latitude' in gps_data.columns and 'Longitude' in gps_data.columns:
                    gps_lat_range = (gps_data['Latitude'].min(), gps_data['Latitude'].max())
                    gps_lon_range = (gps_data['Longitude'].min(), gps_data['Longitude'].max())
                    
                    sat_lat_range = (sat_data['Latitude'].min(), sat_data['Latitude'].max())
                    sat_lon_range = (sat_data['Longitude'].min(), sat_data['Longitude'].max())
                    
                    # Check if GPS trajectory is within reasonable distance of Swarm orbit
                    lat_overlap = (min(gps_lat_range[1], sat_lat_range[1]) > 
                                 max(gps_lat_range[0], sat_lat_range[0]))
                    lon_overlap = (min(gps_lon_range[1], sat_lon_range[1]) > 
                                 max(gps_lon_range[0], sat_lon_range[0]))
                    
                    coverage_stats['spatial_overlap'][sat] = lat_overlap and lon_overlap
        
        # Assess overall coverage quality
        if satellites_with_data == 0:
            coverage_stats['coverage_quality'] = 'no_data'
        elif satellites_with_data == 1:
            coverage_stats['coverage_quality'] = 'limited'
        elif satellites_with_data == 2:
            coverage_stats['coverage_quality'] = 'good'
        else:
            coverage_stats['coverage_quality'] = 'excellent'
        
        # Log coverage summary
        logger.info(f"Data coverage: {satellites_with_data}/3 satellites, "
                   f"quality: {coverage_stats['coverage_quality']}")
        
        if total_overlap_hours < 1:
            logger.warning("Limited temporal overlap between GPS and Swarm data")
        
    except Exception as e:
        logger.error(f"Error checking data coverage: {str(e)}")
        coverage_stats['coverage_quality'] = 'error'
    
    return coverage_stats


def validate_output_file(output_path: Path) -> None:
    """
    Validate the output file after processing.
    
    Args:
        output_path: Path to output CSV file
        
    Raises:
        ValidationError: If output file is invalid
    """
    if not output_path.exists():
        raise ValidationError(f"Output file not created: {output_path}")
    
    try:
        # Read the output file
        result_data = pd.read_csv(output_path)
        
        if result_data.empty:
            raise ValidationError("Output file is empty")
        
        # Check for expected magnetic field columns
        expected_columns = ['N', 'E', 'C', 'H', 'D', 'I', 'F']
        missing_columns = [col for col in expected_columns if col not in result_data.columns]
        
        if missing_columns:
            logger.warning(f"Output file missing expected columns: {missing_columns}")
        
        # Check data types
        numeric_columns = ['N', 'E', 'C', 'H', 'D', 'I', 'F']
        for col in numeric_columns:
            if col in result_data.columns:
                if not pd.api.types.is_numeric_dtype(result_data[col]):
                    logger.warning(f"Column '{col}' is not numeric type")
        
        # Check for excessive NaN values
        total_points = len(result_data)
        for col in expected_columns:
            if col in result_data.columns:
                nan_count = result_data[col].isna().sum()
                nan_percentage = (nan_count / total_points) * 100
                
                if nan_percentage > 50:
                    logger.warning(f"Column '{col}' has {nan_percentage:.1f}% NaN values")
        
        logger.info(f"Output file validation passed: {len(result_data)} points written to {output_path}")
        
    except Exception as e:
        raise ValidationError(f"Failed to validate output file: {str(e)}")


# Quality assessment functions
def assess_interpolation_quality(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Assess the quality of interpolation results.
    
    Args:
        results: List of interpolation results
        
    Returns:
        Dictionary with quality metrics
    """
    quality_metrics = {
        'avg_points_used': 0.0,
        'min_points_used': 0,
        'max_points_used': 0,
        'avg_min_distance': 0.0,
        'success_rate': 0.0,
        'spatial_coverage': 0.0
    }
    
    if not results:
        return quality_metrics
    
    valid_results = [r for r in results if not np.isnan(r.get('N_res', np.nan))]
    
    if not valid_results:
        return quality_metrics
    
    points_used = [r['TotalPoints'] for r in valid_results]
    min_distances = [r.get('Minimum_Distance', np.nan) for r in valid_results if not np.isnan(r.get('Minimum_Distance', np.nan))]
    
    quality_metrics.update({
        'avg_points_used': np.mean(points_used),
        'min_points_used': np.min(points_used),
        'max_points_used': np.max(points_used),
        'success_rate': len(valid_results) / len(results),
    })
    
    if min_distances:
        quality_metrics['avg_min_distance'] = np.mean(min_distances)
    
    logger.info(f"Interpolation quality: {quality_metrics['success_rate']:.1%} success rate, "
               f"avg {quality_metrics['avg_points_used']:.1f} points used")
    
    return quality_metrics