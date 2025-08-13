# Basic Usage

This guide covers the fundamental concepts and basic usage patterns for MagGeo.

## Overview

MagGeo annotates GPS trajectories with geomagnetic field data from ESA's Swarm satellite constellation. The basic workflow involves:

1. **Prepare GPS data** in CSV format
2. **Configure parameters** for your analysis
3. **Run annotation** to add magnetic field data
4. **Analyze results** with comprehensive geomagnetic information

## GPS Data Requirements

### Required Columns

Your GPS trajectory CSV file must contain:

- **Latitude**: Decimal degrees (-90 to +90)
- **Longitude**: Decimal degrees (-180 to +180)  
- **Timestamp**: Date and time information
- **Optional**: Height/altitude, individual/track ID

### Supported Formats

```csv
timestamp,latitude,longitude,height,individual_id
2020-01-01 12:00:00,-45.123,123.456,100.5,bird_001
2020-01-01 12:01:00,-45.124,123.457,101.2,bird_001
2020-01-01 12:02:00,-45.125,123.458,99.8,bird_001
```

### Common Column Names

MagGeo accepts various column name formats:

| Data Type | Accepted Names |
|-----------|----------------|
| Latitude | `latitude`, `lat`, `y` |
| Longitude | `longitude`, `long`, `lon`, `x` |
| Timestamp | `timestamp`, `datetime`, `time`, `date_time` |
| Height | `height`, `altitude`, `alt`, `z` |

## Basic Configuration

### Minimal Parameters

```python
import maggeo

params = {
    'data_dir': 'data',                    # Directory containing GPS file
    'gpsfilename': 'trajectory.csv',       # GPS file name
    'lat_col': 'latitude',                 # Latitude column name
    'long_col': 'longitude',               # Longitude column name
    'datetime_col': 'timestamp',           # Timestamp column name
    'token': 'your_vires_token'            # VirES access token
}

# Run annotation
result = maggeo.annotate_gps_with_geomag(params)
```

### Extended Parameters

```python
params = {
    # Required
    'data_dir': 'data',
    'gpsfilename': 'bird_trajectory.csv',
    'lat_col': 'lat',
    'long_col': 'lon', 
    'datetime_col': 'time',
    'token': 'your_vires_token',
    
    # Optional - Performance
    'parallel': True,                      # Enable parallel processing
    'n_cores': 4,                         # Number of CPU cores
    
    # Optional - Data Management
    'use_swarm_manager': True,            # Use persistent storage
    'swarm_data_dir': 'swarm_cache',      # Storage directory
    'swarm_manager_format': 'parquet',    # Storage format
    
    # Optional - Quality Control
    'quality_check': True,                # Validate data quality
    'remove_outliers': False,             # Remove statistical outliers
    
    # Optional - Processing
    'satellites': ['A', 'B', 'C'],       # Swarm satellites to use
    'interpolation_method': 'linear',     # Interpolation method
    'include_indices': True,              # Add geomagnetic indices
    'indices': ['AE', 'SME']              # Which indices to include
}

result = maggeo.annotate_gps_with_geomag(params)
```

## Understanding the Output

### Output Structure

The annotated data contains your original GPS data plus magnetic field information:

```python
print(result.columns.tolist())
# ['timestamp', 'location-long', 'location-lat', 'height', 'individual_id',
#  'TotalPoints', 'Minimum_Distance', 'Average_Distance', 'Kp',
#  'N', 'E', 'C', 'N_Obs', 'E_Obs', 'C_Obs', 'H', 'D', 'I', 'F']
```

### Column Descriptions

#### Original GPS Data
- `timestamp`: Your original timestamp
- `location-lat`, `location-long`: GPS coordinates
- `height`: Altitude (if provided)
- `individual_id`: Track identifier (if provided)

#### Trajectory Statistics
- `TotalPoints`: Total points in trajectory
- `Minimum_Distance`: Minimum distance between consecutive points (meters)
- `Average_Distance`: Average distance between consecutive points (meters)

#### Geomagnetic Activity
- `Kp`: Planetary K-index (0-9 scale, geomagnetic activity level)

#### Magnetic Field Components (NEC Frame)
- `N`: North component (nT) - CHAOS model
- `E`: East component (nT) - CHAOS model
- `C`: Center/Down component (nT) - CHAOS model

#### Observed Components
- `N_Obs`: North component from Swarm observations (nT)
- `E_Obs`: East component from Swarm observations (nT)
- `C_Obs`: Center component from Swarm observations (nT)

#### Derived Parameters
- `H`: Horizontal intensity = √(N² + E²) (nT)
- `D`: Magnetic declination = arctan(E/N) (degrees)
- `I`: Magnetic inclination = arctan(C/H) (degrees)
- `F`: Total intensity = √(N² + E² + C²) (nT)

## Basic Analysis Examples

### View Summary Statistics

```python
# Basic trajectory info
print(f"Trajectory summary:")
print(f"  Total points: {len(result):,}")
print(f"  Duration: {result['timestamp'].max() - result['timestamp'].min()}")
print(f"  Average distance: {result['Average_Distance'].iloc[0]:.1f} meters")

# Magnetic field statistics
print(f"\nMagnetic field summary:")
print(f"  Total field range: {result['F'].min():.0f} - {result['F'].max():.0f} nT")
print(f"  Average total field: {result['F'].mean():.1f} nT")
print(f"  Horizontal field: {result['H'].mean():.1f} nT")

# Geomagnetic activity
print(f"\nGeomagnetic activity:")
print(f"  Kp range: {result['Kp'].min():.1f} - {result['Kp'].max():.1f}")
print(f"  Average Kp: {result['Kp'].mean():.2f}")

if result['Kp'].mean() < 3:
    print("  Conditions: Quiet")
elif result['Kp'].mean() < 5:
    print("  Conditions: Active") 
else:
    print("  Conditions: Disturbed")
```

### Simple Visualization

```python
import matplotlib.pyplot as plt

# Create basic plots
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Trajectory map
axes[0,0].plot(result['location-long'], result['location-lat'], 'b-', alpha=0.7)
axes[0,0].set_xlabel('Longitude')
axes[0,0].set_ylabel('Latitude')
axes[0,0].set_title('GPS Trajectory')
axes[0,0].grid(True, alpha=0.3)

# Total magnetic field
axes[0,1].plot(result['timestamp'], result['F'], 'r-', alpha=0.8)
axes[0,1].set_xlabel('Time')
axes[0,1].set_ylabel('Total Field F (nT)')
axes[0,1].set_title('Magnetic Field Intensity')
axes[0,1].tick_params(axis='x', rotation=45)
axes[0,1].grid(True, alpha=0.3)

# Geomagnetic activity
axes[1,0].plot(result['timestamp'], result['Kp'], 'g-', linewidth=2)
axes[1,0].set_xlabel('Time')
axes[1,0].set_ylabel('Kp Index')
axes[1,0].set_title('Geomagnetic Activity')
axes[1,0].tick_params(axis='x', rotation=45)
axes[1,0].grid(True, alpha=0.3)

# Magnetic declination
axes[1,1].plot(result['timestamp'], result['D'], 'purple', alpha=0.8)
axes[1,1].set_xlabel('Time')
axes[1,1].set_ylabel('Declination (degrees)')
axes[1,1].set_title('Magnetic Declination')
axes[1,1].tick_params(axis='x', rotation=45)
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## Common Workflows

### Workflow 1: Quick Analysis

```python
# Quick one-shot analysis
import maggeo

params = {
    'data_dir': 'data',
    'gpsfilename': 'my_trajectory.csv',
    'lat_col': 'latitude',
    'long_col': 'longitude',
    'datetime_col': 'timestamp',
    'token': 'your_vires_token'
}

result = maggeo.annotate_gps_with_geomag(params)

# Save results
result.to_csv('annotated_trajectory.csv', index=False)
print("✅ Results saved to annotated_trajectory.csv")
```

### Workflow 2: Persistent Storage

```python
# For repeated analysis or multiple trajectories
from maggeo import SwarmDataManager

# Setup persistent storage
manager = SwarmDataManager("swarm_data", file_format="parquet")

# Load GPS data
import pandas as pd
gps_df = pd.read_csv('trajectory.csv')
gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'])

# Download Swarm data (once)
swarm_a, swarm_b, swarm_c = manager.download_for_trajectory(
    gps_df, token='your_vires_token'
)

# Later analysis sessions load instantly
data = manager.load_concatenated_data(['A', 'B', 'C'])
print("⚡ Loaded from storage - much faster!")
```

### Workflow 3: Large Dataset Processing

```python
# For large trajectories (10,000+ points)
params = {
    'data_dir': 'data',
    'gpsfilename': 'large_trajectory.csv',
    'lat_col': 'latitude',
    'long_col': 'longitude',
    'datetime_col': 'timestamp',
    'token': 'your_vires_token',
    
    # Enable optimization for large datasets
    'parallel': True,               # Use multiple CPU cores
    'n_cores': 4,                  # Adjust based on your system
    'use_swarm_manager': True,     # Persistent storage
    'swarm_data_dir': 'swarm_cache'
}

result = maggeo.annotate_gps_with_geomag(params)
```

## Data Quality Considerations

### Check Data Completeness

```python
# Check for missing values
missing_data = result.isnull().sum()
print("Missing data per column:")
print(missing_data[missing_data > 0])

# Check magnetic field data quality
complete_f = (~result['F'].isna()).sum()
print(f"Complete F measurements: {complete_f}/{len(result)} ({complete_f/len(result)*100:.1f}%)")
```

### Validate Results

```python
# Check reasonable magnetic field ranges
f_range = [result['F'].min(), result['F'].max()]
print(f"Total field range: {f_range[0]:.0f} - {f_range[1]:.0f} nT")

# Typical Earth magnetic field: 25,000 - 65,000 nT
if f_range[0] < 20000 or f_range[1] > 70000:
    print("⚠️ Warning: Magnetic field values outside typical Earth range")
else:
    print("✅ Magnetic field values within expected range")

# Check Kp index range
kp_range = [result['Kp'].min(), result['Kp'].max()]
print(f"Kp range: {kp_range[0]:.1f} - {kp_range[1]:.1f}")

if kp_range[1] > 9:
    print("⚠️ Warning: Kp values above maximum scale")
else:
    print("✅ Kp values within valid range")
```

## Troubleshooting

### Common Issues

#### Issue: "File not found"
```python
# Check file path and name
import os
file_path = os.path.join(params['data_dir'], params['gpsfilename'])
if os.path.exists(file_path):
    print(f"✅ File found: {file_path}")
else:
    print(f"❌ File not found: {file_path}")
    print(f"Available files: {os.listdir(params['data_dir'])}")
```

#### Issue: "Column not found"
```python
# Check available columns
import pandas as pd
gps_df = pd.read_csv(os.path.join(params['data_dir'], params['gpsfilename']))
print(f"Available columns: {gps_df.columns.tolist()}")

# Update column names
params['lat_col'] = 'lat'  # Adjust as needed
params['long_col'] = 'lon'
params['datetime_col'] = 'time'
```

#### Issue: "Invalid VirES token"
```python
# Test token validity
try:
    from viresclient import SwarmRequest
    request = SwarmRequest()
    request.set_token(token=params['token'])
    print("✅ VirES token is valid")
except Exception as e:
    print(f"❌ VirES token error: {e}")
    print("Get a new token at: https://vires.services/")
```

### Performance Tips

#### For Small Datasets (< 1,000 points)
- Use default settings
- No need for parallel processing
- CSV format is fine

#### For Medium Datasets (1,000 - 10,000 points)
- Consider using SwarmDataManager
- Parquet format recommended
- Parallel processing optional

#### For Large Datasets (> 10,000 points)
- Always use SwarmDataManager
- Enable parallel processing
- Use Parquet format
- Consider processing in chunks

## Next Steps

- **Advanced Features**: See [SwarmDataManager Guide](../api/swarm_data_manager.md) for persistent storage
- **Performance**: Check [Parallel Processing Guide](../api/parallel_processing.md) for large datasets
- **Examples**: View [Basic Examples](../examples/basic.md) for practical use cases
- **API Reference**: Consult [Core Functions](../api/core.md) for detailed documentation
