"""
Command Line Interface for MagGeo package.

This module provides CLI commands for GPS trajectory annotation with geomagnetic data.
"""

import click
import pandas as pd
import os
from pathlib import Path
from .core import annotate_gps_with_geomag
from .swarm_data_manager import SwarmDataManager
from .parallel_processing import parallel_maggeo_annotation
from . import __version__


@click.group()
@click.version_option(version=__version__, prog_name="maggeo")
def main():
    """MagGeo: GPS trajectory annotation with geomagnetic data from Swarm satellites."""
    pass


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), 
              help='Output file path (default: input_file_annotated.csv)')
@click.option('--lat-col', default='latitude', 
              help='Column name for latitude (default: latitude)')
@click.option('--lon-col', default='longitude', 
              help='Column name for longitude (default: longitude)')
@click.option('--datetime-col', default='datetime', 
              help='Column name for datetime (default: datetime)')
@click.option('--altitude-col', default=None, 
              help='Column name for altitude (optional)')
@click.option('--parallel', is_flag=True, 
              help='Use parallel processing for large files')
@click.option('--chunk-size', default=1000, type=int,
              help='Chunk size for parallel processing (default: 1000)')
def annotate(input_file, output, lat_col, lon_col, datetime_col, altitude_col, parallel, chunk_size):
    """Annotate GPS trajectory with geomagnetic data."""
    
    if output is None:
        input_path = Path(input_file)
        output = input_path.parent / f"{input_path.stem}_annotated{input_path.suffix}"
    
    click.echo(f"Reading GPS data from: {input_file}")
    
    try:
        # Read GPS data
        gps_df = pd.read_csv(input_file)
        
        # Validate required columns
        required_cols = [lat_col, lon_col, datetime_col]
        missing_cols = [col for col in required_cols if col not in gps_df.columns]
        if missing_cols:
            raise click.ClickException(f"Missing required columns: {missing_cols}")
        
        click.echo(f"Processing {len(gps_df)} GPS points...")
        
        if parallel and len(gps_df) > chunk_size:
            click.echo("Using parallel processing...")
            annotated_df = parallel_maggeo_annotation(
                gps_df, 
                lat_col=lat_col,
                lon_col=lon_col,
                datetime_col=datetime_col,
                altitude_col=altitude_col,
                chunk_size=chunk_size
            )
        else:
            # Use single-threaded processing
            annotated_df = annotate_gps_with_geomag(
                gps_df,
                lat_col=lat_col,
                lon_col=lon_col,
                datetime_col=datetime_col,
                altitude_col=altitude_col
            )
        
        # Save results
        annotated_df.to_csv(output, index=False)
        click.echo(f"Annotated trajectory saved to: {output}")
        click.echo(f"Added {len(annotated_df.columns) - len(gps_df.columns)} geomagnetic columns")
        
    except Exception as e:
        raise click.ClickException(f"Error processing file: {str(e)}")


@main.command()
@click.option('--start-date', required=True, type=str,
              help='Start date (YYYY-MM-DD format)')
@click.option('--end-date', required=True, type=str,
              help='End date (YYYY-MM-DD format)')
@click.option('--output-dir', '-o', type=click.Path(),
              help='Output directory for Swarm data (default: ./swarm_data)')
@click.option('--satellites', default='A,B,C',
              help='Comma-separated list of Swarm satellites (default: A,B,C)')
@click.option('--data-type', default='MAG',
              help='Swarm data type (default: MAG)')
def swarm(start_date, end_date, output_dir, satellites, data_type):
    """Download and manage Swarm satellite data."""
    
    if output_dir is None:
        output_dir = './swarm_data'
    
    satellite_list = [sat.strip() for sat in satellites.split(',')]
    
    click.echo(f"Downloading Swarm data from {start_date} to {end_date}")
    click.echo(f"Satellites: {satellite_list}")
    click.echo(f"Output directory: {output_dir}")
    
    try:
        manager = SwarmDataManager()
        
        for satellite in satellite_list:
            click.echo(f"Processing Swarm-{satellite}...")
            data = manager.download_swarm_data(
                start_date=start_date,
                end_date=end_date,
                satellite=satellite,
                data_type=data_type
            )
            
            output_file = os.path.join(output_dir, f"swarm_{satellite}_{start_date}_{end_date}.parquet")
            os.makedirs(output_dir, exist_ok=True)
            data.to_parquet(output_file)
            
            click.echo(f"Saved {len(data)} records to {output_file}")
        
        click.echo("Swarm data download completed!")
        
    except Exception as e:
        raise click.ClickException(f"Error downloading Swarm data: {str(e)}")


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
def validate(input_file):
    """Validate GPS trajectory file format."""
    
    click.echo(f"Validating GPS file: {input_file}")
    
    try:
        df = pd.read_csv(input_file)
        
        click.echo(f"File contains {len(df)} rows and {len(df.columns)} columns")
        click.echo(f"Columns: {list(df.columns)}")
        
        # Check for common GPS column names
        common_lat_cols = ['latitude', 'lat', 'location-lat', 'Latitude']
        common_lon_cols = ['longitude', 'lon', 'location-long', 'Longitude']
        common_time_cols = ['datetime', 'timestamp', 'time', 'Date_Time']
        
        lat_col = next((col for col in common_lat_cols if col in df.columns), None)
        lon_col = next((col for col in common_lon_cols if col in df.columns), None)
        time_col = next((col for col in common_time_cols if col in df.columns), None)
        
        if lat_col:
            click.echo(f"✓ Found latitude column: {lat_col}")
        else:
            click.echo("✗ No latitude column detected")
            
        if lon_col:
            click.echo(f"✓ Found longitude column: {lon_col}")
        else:
            click.echo("✗ No longitude column detected")
            
        if time_col:
            click.echo(f"✓ Found datetime column: {time_col}")
        else:
            click.echo("✗ No datetime column detected")
        
        if lat_col and lon_col and time_col:
            click.echo("✓ File appears to be compatible with MagGeo")
            click.echo(f"Suggested command:")
            click.echo(f"maggeo annotate {input_file} --lat-col {lat_col} --lon-col {lon_col} --datetime-col {time_col}")
        else:
            click.echo("✗ File may need column name adjustments")
            
    except Exception as e:
        raise click.ClickException(f"Error validating file: {str(e)}")


@main.command()
def info():
    """Display MagGeo package information."""
    
    click.echo(f"MagGeo version: {__version__}")
    click.echo("A Python package for fusing GPS trajectories with geomagnetic data")
    click.echo("")
    click.echo("Authors: Fernando Benitez-Paez, Urška Demšar, Jed Long, Ciaran Beggan")
    click.echo("Citation: Benitez-Paez et al. (2021) Movement Ecology 9:31")
    click.echo("Repository: https://github.com/MagGeo/MagGeo")
    click.echo("")
    click.echo("Available commands:")
    click.echo("  annotate  - Annotate GPS trajectories with geomagnetic data")
    click.echo("  swarm     - Download and manage Swarm satellite data")
    click.echo("  validate  - Validate GPS file format")
    click.echo("  info      - Display this information")


if __name__ == '__main__':
    main()
