# Core Functions

The core module provides the main functionality for MagGeo, including the primary function for annotating GPS trajectories with geomagnetic field data.

::: maggeo.core

## Main Functions

### annotate_gps_with_geomag

::: maggeo.core.annotate_gps_with_geomag
    options:
      show_root_heading: false

**Example Usage:**

```python
import maggeo

# Basic parameters
params = {
    'data_dir': 'data/sample_data',
    'gpsfilename': 'BirdGPSTrajectory.csv',
    'lat_col': 'latitude',
    'long_col': 'longitude',
    'datetime_col': 'timestamp',
    'token': 'your_vires_token'
}

# Annotate trajectory
result = maggeo.annotate_gps_with_geomag(params)
print(f"Annotated {len(result)} GPS points with magnetic field data")
```

**Advanced Usage:**

```python
# With SwarmDataManager for persistent storage
params.update({
    'use_swarm_manager': True,
    'swarm_data_dir': 'persistent_swarm_data',
    'swarm_manager_format': 'parquet'
})

# With parallel processing
params.update({
    'parallel': True,
    'n_cores': 4
})

result = maggeo.annotate_gps_with_geomag(params)
```

## Configuration Parameters

The main function `annotate_gps_with_geomag` accepts a comprehensive set of parameters:

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `data_dir` | str | Directory containing GPS data |
| `gpsfilename` | str | Name of GPS trajectory CSV file |
| `lat_col` | str | Column name for latitude values |
| `long_col` | str | Column name for longitude values |
| `datetime_col` | str | Column name for datetime values |
| `token` | str | VirES authentication token |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_swarm_manager` | bool | False | Use SwarmDataManager for storage |
| `swarm_data_dir` | str | None | Directory for SwarmDataManager |
| `parallel` | bool | False | Enable parallel processing |
| `n_cores` | int | None | Number of CPU cores |
| `interpolation_method` | str | 'linear' | Interpolation method |
| `satellites` | list | ['A', 'B', 'C'] | Swarm satellites to use |
| `quality_check` | bool | True | Perform data quality validation |

## Return Data Structure

The annotated GPS data includes these columns:

## Return Data Structure

The annotated GPS data includes these columns:

### Original GPS Data
- `timestamp`: Original timestamp column
- `location-long`: Longitude values (degrees)
- `location-lat`: Latitude values (degrees) 
- `height`: Height/altitude values (if present)
- `individual_id`: Individual/track identifier (if present)

### Trajectory Statistics
- `TotalPoints`: Total number of points in trajectory
- `Minimum_Distance`: Minimum distance between consecutive points (meters)
- `Average_Distance`: Average distance between consecutive points (meters)

### Geomagnetic Activity Index
- `Kp`: Planetary K-index indicating geomagnetic activity level (0-9 scale)

### Magnetic Field Components (NEC Frame)
- `N`: North component of magnetic field (nT)
- `E`: East component of magnetic field (nT)  
- `C`: Center/Down component of magnetic field (nT)

### Observed Magnetic Field Components
- `N_Obs`: Observed North component from Swarm satellites (nT)
- `E_Obs`: Observed East component from Swarm satellites (nT)
- `C_Obs`: Observed Center/Down component from Swarm satellites (nT)

### Derived Magnetic Parameters
- `H`: Horizontal magnetic field intensity (nT)
- `D`: Magnetic declination (degrees)
- `I`: Magnetic inclination (degrees)
- `F`: Total magnetic field intensity (nT)

## Example Output

```python
# Example of annotated trajectory structure
print(result.columns.tolist())
# ['timestamp', 'location-long', 'location-lat', 'height', 'individual_id',
#  'TotalPoints', 'Minimum_Distance', 'Average_Distance', 'Kp',
#  'N', 'E', 'C', 'N_Obs', 'E_Obs', 'C_Obs', 'H', 'D', 'I', 'F']

# Sample data point
print(result.iloc[0])
# timestamp               08/09/2014 06:10
# location-long           67.97505
# location-lat            70.8303
# height                  0.406
# individual_id           1
# TotalPoints             46
# Minimum_Distance        340.04
# Average_Distance        667.15
# Kp                      1.67
# N                       6989.98
# E                       3866.52
# C                       57646.92
# N_Obs                   7009.43
# E_Obs                   3854.00
# C_Obs                   57636.83
# H                       7988.11
# D                       28.95
# I                       82.11
# F                       58197.75
```

## Data Interpretation

### Coordinate Systems

**NEC Frame (North-East-Center):**
- **N**: Positive northward
- **E**: Positive eastward  
- **C**: Positive downward (toward Earth's center)

**Classical Magnetic Elements:**
- **H**: Horizontal intensity = √(N² + E²)
- **D**: Declination = arctan(E/N) - angle from geographic north
- **I**: Inclination = arctan(C/H) - angle from horizontal
- **F**: Total intensity = √(N² + E² + C²)

### Quality Assessment

The difference between model values (`N`, `E`, `C`) and observed values (`N_Obs`, `E_Obs`, `C_Obs`) indicates:
- **Small differences**: Good model-observation agreement
- **Large differences**: Possible local anomalies, data quality issues, or significant magnetic disturbances

### Geomagnetic Activity

**Kp Index Interpretation:**
- **0-2**: Quiet conditions
- **3-4**: Unsettled to active
- **5-6**: Minor to moderate geomagnetic storm
- **7-9**: Strong to extreme geomagnetic storm