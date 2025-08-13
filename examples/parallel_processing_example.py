"""
Example usage of MagGeo with parallel processing capabilities.

This script demonstrates how to use the new parallel processing features
for faster processing of large GPS trajectory datasets.
"""

import pandas as pd
import time
import multiprocessing as mp
from maggeo import annotate_gps_with_geomag, parallel_row_handler
from maggeo.parallel_processing import parallel_interpolation, parallel_chaos_calculation


def example_parallel_usage():
    """
    Example showing how to use MagGeo with parallel processing.
    """
    
    # Configuration parameters
    params = {
        'data_dir': 'data/sample_data/',
        'gpsfilename': 'BirdGPSTrajectory.csv',
        'lat_col': 'location-lat',
        'long_col': 'location-long', 
        'datetime_col': 'timestamp',
        'altitude_col': 'height-above-ellipsoid',
        'token': 'your_esa_swarm_token',  # Replace with your actual token
        'swarm_data_dir': 'temp_data/swarm_data',
        'dt_seconds': 14400,  # 4 hours time window
        'chunk_size': 1000    # Process 1000 GPS points per chunk
    }
    
    print("=== MagGeo Parallel Processing Example ===")
    print(f"Available CPU cores: {mp.cpu_count()}")
    
    # Method 1: Use the main function with parallel processing enabled
    print("\n1. Using main function with parallel processing:")
    start_time = time.time()
    
    result_parallel = annotate_gps_with_geomag(
        params=params,
        use_swarm_manager=True,  # Use SwarmDataManager for efficient data handling
        use_parallel=True,       # Enable parallel processing
        n_cores=4               # Use 4 cores (adjust based on your system)
    )
    
    parallel_time = time.time() - start_time
    print(f"Parallel processing completed in {parallel_time:.2f} seconds")
    print(f"Processed {len(result_parallel)} GPS points")
    
    # Method 2: Compare with sequential processing (for smaller datasets)
    print("\n2. Comparison with sequential processing:")
    start_time = time.time()
    
    result_sequential = annotate_gps_with_geomag(
        params=params,
        use_swarm_manager=True,  # Use SwarmDataManager for efficient data handling
        use_parallel=False       # Disable parallel processing
    )
    
    sequential_time = time.time() - start_time
    print(f"Sequential processing completed in {sequential_time:.2f} seconds")
    
    # Performance comparison
    if sequential_time > 0:
        speedup = sequential_time / parallel_time
        print(f"\nSpeedup: {speedup:.2f}x faster with parallel processing")
    
    # Method 3: Manual parallel processing (advanced usage)
    print("\n3. Manual parallel processing workflow:")
    
    # Load GPS data manually
    from maggeo.gps import get_gps_data
    from maggeo.swarm_data_manager import SwarmDataManager
    
    gps_df = get_gps_data(
        data_dir=params['data_dir'],
        gpsfilename=params['gpsfilename'],
        lat_col=params['lat_col'],
        lon_col=params['long_col'],
        datetime_col=params['datetime_col'],
        altitude_col=params.get('altitude_col', None)
    )
    
    # Load Swarm data using SwarmDataManager
    swarm_manager = SwarmDataManager(
        data_dir=params['swarm_data_dir'],
        token=params['token']
    )
    swarm_a, swarm_b, swarm_c = swarm_manager.download_for_trajectory(gps_df)
    
    # Manual parallel processing
    start_time = time.time()
    
    # Step 1: Parallel interpolation
    interpolated_df = parallel_interpolation(
        gps_df, swarm_a, swarm_b, swarm_c,
        dt_seconds=params['dt_seconds'],
        n_cores=4,
        chunk_size=params['chunk_size']
    )
    
    # Step 2: Parallel CHAOS calculation
    final_df = parallel_chaos_calculation(
        interpolated_df,
        n_cores=4,
        chunk_size=params['chunk_size']
    )
    
    manual_time = time.time() - start_time
    print(f"Manual parallel processing completed in {manual_time:.2f} seconds")
    
    return result_parallel


def benchmark_parallel_processing():
    """
    Benchmark parallel processing performance with different core counts.
    """
    print("\n=== Parallel Processing Benchmark ===")
    
    # Test with different numbers of cores
    core_counts = [1, 2, 4, mp.cpu_count()]
    
    params = {
        'data_dir': 'data/sample_data/',
        'gpsfilename': 'BirdGPSTrajectory.csv',
        'lat_col': 'location-lat',
        'long_col': 'location-long', 
        'datetime_col': 'timestamp',
        'altitude_col': 'height-above-ellipsoid',
        'token': 'your_esa_swarm_token',
        'chunk_size': 500
    }
    
    for n_cores in core_counts:
        print(f"\nTesting with {n_cores} cores:")
        start_time = time.time()
        
        try:
            result = annotate_gps_with_geomag(
                params=params,
                use_swarm_manager=True,
                use_parallel=True,
                n_cores=n_cores
            )
            
            processing_time = time.time() - start_time
            print(f"  Time: {processing_time:.2f} seconds")
            print(f"  GPS points processed: {len(result)}")
            
        except Exception as e:
            print(f"  Error: {e}")


def memory_efficient_processing():
    """
    Example of memory-efficient processing for very large datasets.
    """
    print("\n=== Memory-Efficient Processing for Large Datasets ===")
    
    params = {
        'data_dir': 'data/sample_data/',
        'gpsfilename': 'BirdGPSTrajectory.csv',
        'lat_col': 'location-lat',
        'long_col': 'location-long', 
        'datetime_col': 'timestamp',
        'altitude_col': 'height-above-ellipsoid',
        'token': 'your_esa_swarm_token',
        'chunk_size': 100  # Smaller chunk size for memory efficiency
    }
    
    # For very large datasets, use smaller chunk sizes and fewer cores
    # to avoid memory issues
    result = annotate_gps_with_geomag(
        params=params,
        use_swarm_manager=True,
        use_parallel=True,
        n_cores=2  # Use fewer cores for memory-intensive tasks
    )
    
    print(f"Processed {len(result)} GPS points with memory-efficient settings")
    
    # Save results incrementally to avoid memory issues
    result.to_csv('maggeo_results_large_dataset.csv', index=False)
    print("Results saved to maggeo_results_large_dataset.csv")


if __name__ == "__main__":
    # Run the example
    try:
        result = example_parallel_usage()
        print("\n=== Processing completed successfully! ===")
        print(f"Final result shape: {result.shape}")
        print(f"Columns: {list(result.columns)}")
        
        # Optionally run benchmarks
        # benchmark_parallel_processing()
        
        # Optionally test memory-efficient processing
        # memory_efficient_processing()
        
    except Exception as e:
        print(f"Error during processing: {e}")
        print("Make sure you have:")
        print("1. Valid ESA Swarm token")
        print("2. GPS data file in the specified location")
        print("3. All required dependencies installed")
