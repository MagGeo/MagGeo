# Swarm Data Manager Usage

How to use the new `SwarmDataManager` for independent Swarm data downloads.

## Basic Usage

### 1. Download and Save Swarm Data for a Trajectory

```python
import maggeo
import pandas as pd

# Load your GPS trajectory
gps_df = maggeo.get_gps_data(
    data_dir="data/sample_data",
    gpsfilename="BirdGPSTrajectory.csv",
    lat_col="latitude",
    lon_col="longitude", 
    datetime_col="timestamp"
)

# Option 1: Using the convenience function
swarm_a, swarm_b, swarm_c = maggeo.download_swarm_data_for_trajectory(
    gps_df,
    data_dir="my_swarm_data",
    file_format="csv",  # or "csv", "pickle"
    token="your_vires_token",
    resume=True  # Skip already downloaded files
)

# Option 2: Using the SwarmDataManager class directly
manager = maggeo.SwarmDataManager(
    data_dir="my_swarm_data",
    file_format="parquet",
    chunk_size=10,  # Process 10 dates at a time
    token="your_vires_token"
)

swarm_a, swarm_b, swarm_c = manager.download_for_trajectory(
    gps_df,
    save_individual_files=True,  # Save daily files
    save_concatenated=True,      # Save concatenated files
    resume=True                  # Resume interrupted downloads
)
```

### 2. Download Data for Specific Dates

```python
import datetime as dt

# Define specific dates
dates = [
    dt.date(2023, 6, 15),
    dt.date(2023, 6, 16),
    dt.date(2023, 6, 17)
]

manager = maggeo.SwarmDataManager(data_dir="my_swarm_data")
swarm_a, swarm_b, swarm_c = manager.download_for_dates(dates)
```

### 3. Load Previously Downloaded Data

```python
# Load concatenated data
data = maggeo.load_swarm_data(
    data_dir="my_swarm_data",
    file_format="parquet",
    satellites=['A', 'B', 'C']
)

swarm_a = data['A']
swarm_b = data['B'] 
swarm_c = data['C']

# Or using the manager
manager = maggeo.SwarmDataManager(data_dir="my_swarm_data")
data = manager.load_concatenated_data(['A', 'B', 'C'])

# Load specific dates
specific_dates = [dt.date(2023, 6, 15), dt.date(2023, 6, 16)]
data = manager.load_data_for_dates(specific_dates, satellites=['A', 'B'])
```

## Advanced Usage

### 1. Data Management and Quality Control

```python
manager = maggeo.SwarmDataManager(data_dir="my_swarm_data")

# Get summary of available data
summary = manager.get_data_summary()
print(summary)
# Shows: satellite, date, filename, file_size_mb, row_count, data_quality

# Clean up old or poor quality data
removed_count = manager.cleanup_data(
    older_than_days=30,      # Remove files older than 30 days
    quality_threshold='fair'  # Remove files with 'poor' quality
)
print(f"Removed {removed_count} files")
```

### 2. Using with the Main MagGeo Pipeline

```python
# Updated main function supports SwarmDataManager
params = {
    'data_dir': 'data/sample_data',
    'gpsfilename': 'BirdGPSTrajectory.csv',
    'lat_col': 'latitude',
    'long_col': 'longitude',
    'datetime_col': 'timestamp',
    'token': 'your_vires_token',
    'swarm_data_dir': 'persistent_swarm_data',  # Where to store Swarm data
    'swarm_file_format': 'parquet',             # Format for Swarm data
    'resume_swarm_download': True               # Resume interrupted downloads
}

# Use SwarmDataManager for better data handling
result = maggeo.annotate_gps_with_geomag(params, use_swarm_manager=True)
```

### 3. Batch Processing Large Trajectories

```python
# For very large trajectories, process in chunks
manager = maggeo.SwarmDataManager(
    data_dir="large_trajectory_data",
    chunk_size=5,  # Smaller chunks for memory efficiency
    file_format="parquet"
)

# Process trajectory in chunks to save memory
unique_dates = maggeo.identify_unique_dates(large_gps_df)['date']
date_chunks = [unique_dates[i:i+5] for i in range(0, len(unique_dates), 5)]

all_swarm_data = {'A': [], 'B': [], 'C': []}

for chunk in date_chunks:
    print(f"Processing chunk with {len(chunk)} dates...")
    swarm_a, swarm_b, swarm_c = manager.download_for_dates(
        chunk, 
        save_individual_files=True,
        save_concatenated=False  # Don't concatenate until the end
    )
    
    all_swarm_data['A'].append(swarm_a)
    all_swarm_data['B'].append(swarm_b)
    all_swarm_data['C'].append(swarm_c)

# Concatenate all chunks at the end
final_swarm_a = pd.concat(all_swarm_data['A'])
final_swarm_b = pd.concat(all_swarm_data['B'])
final_swarm_c = pd.concat(all_swarm_data['C'])

# Save final concatenated data
manager._save_concatenated_data(final_swarm_a, final_swarm_b, final_swarm_c)
```

## Use Cases

### 1. Pre-download Data for Multiple Analyses

```python
# Download data once for a study area/time period
study_dates = pd.date_range('2023-06-01', '2023-06-30', freq='D').date

manager = maggeo.SwarmDataManager(data_dir="study_area_swarm_data")
swarm_a, swarm_b, swarm_c = manager.download_for_dates(study_dates)

# Later, use this data for multiple GPS trajectories without re-downloading
for trajectory_file in ['bird1.csv', 'bird2.csv', 'bird3.csv']:
    # Load existing Swarm data
    data = manager.load_concatenated_data()
    
    # Process trajectory with pre-downloaded data
    # ... your analysis code here
```

### 2. Resume Interrupted Downloads

```python
# If download was interrupted, just run again with resume=True
manager = maggeo.SwarmDataManager(data_dir="my_swarm_data")

# This will skip already downloaded files and continue where it left off
swarm_a, swarm_b, swarm_c = manager.download_for_trajectory(
    gps_df, 
    resume=True
)
```

### 3. Different File Formats for Different Use Cases

```python
# Use CSV for human-readable files
csv_manager = maggeo.SwarmDataManager(
    data_dir="human_readable_data",
    file_format="csv"
)

# Use Parquet for efficient storage and fast loading
parquet_manager = maggeo.SwarmDataManager(
    data_dir="efficient_data", 
    file_format="parquet"
)

# Use Pickle for preserving exact pandas data types
pickle_manager = maggeo.SwarmDataManager(
    data_dir="exact_data",
    file_format="pickle"
)
```

## File Organization

The SwarmDataManager creates the following directory structure:

```
my_swarm_data/
├── swarm_A/
│   ├── swarm_A_2023-06-15.parquet
│   ├── swarm_A_2023-06-16.parquet
│   └── ...
├── swarm_B/
│   ├── swarm_B_2023-06-15.parquet
│   ├── swarm_B_2023-06-16.parquet
│   └── ...
├── swarm_C/
│   ├── swarm_C_2023-06-15.parquet
│   ├── swarm_C_2023-06-16.parquet
│   └── ...
├── swarm_A_concatenated.parquet
├── swarm_B_concatenated.parquet
└── swarm_C_concatenated.parquet
```

This structure allows for:
- Easy resuming of interrupted downloads
- Efficient loading of specific date ranges
- Quick access to full datasets via concatenated files
- Easy data management and cleanup

## Error Handling

The SwarmDataManager includes robust error handling:

```python
import warnings

# Failed downloads are logged but don't stop the process
with warnings.catch_warnings():
    warnings.simplefilter("always")  # Show warning messages
    
    swarm_a, swarm_b, swarm_c = manager.download_for_trajectory(gps_df)
    
# Check data quality
summary = manager.get_data_summary()
poor_quality_data = summary[summary['data_quality'] == 'poor']
if not poor_quality_data.empty:
    print("Warning: Some data has poor quality:")
    print(poor_quality_data)
```
