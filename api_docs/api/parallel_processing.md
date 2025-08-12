# Parallel Processing

The parallel_processing module provides utilities for efficient parallel computation of MagGeo's geomagnetic field analysis pipeline, enabling faster processing of large GPS trajectories.

::: maggeo.parallel_processing

## Overview

This module implements parallel processing strategies specifically optimized for MagGeo's workflow:

- **GPS Trajectory Chunking**: Split large GPS trajectories for parallel processing
- **Complete Swarm Data Access**: Each worker process gets access to complete Swarm datasets
- **Proper Interpolation**: Ensures each GPS point can find matches across all Swarm data
- **Integrated Pipeline**: Handles interpolation, CHAOS calculations, and component derivation

## Key Functions

### parallel_maggeo_annotation

::: maggeo.parallel_processing.parallel_maggeo_annotation
    options:
      show_root_heading: false

**Example:**

```python
from maggeo.parallel_processing import parallel_maggeo_annotation
import pandas as pd

# Load GPS trajectory and Swarm data
gps_df = pd.read_csv('large_trajectory.csv')
swarm_a = pd.read_csv('swarm_a_data.csv')
swarm_b = pd.read_csv('swarm_b_data.csv') 
swarm_c = pd.read_csv('swarm_c_data.csv')

# Process in parallel
result = parallel_maggeo_annotation(
    gps_df=gps_df,
    swarm_a=swarm_a,
    swarm_b=swarm_b,
    swarm_c=swarm_c,
    dt_seconds=14400,  # 4-hour time window
    n_cores=4,
    chunk_size=100
)

print(f"Processed {len(result)} points using 4 cores")
```

### get_optimal_chunk_size

::: maggeo.parallel_processing.get_optimal_chunk_size
    options:
      show_root_heading: false

**Example:**

```python
# Calculate optimal chunk size
chunk_size = get_optimal_chunk_size(
    total_gps_points=50000,
    n_cores=4,
    min_chunk_size=50
)
print(f"Optimal chunk size: {chunk_size}")
```

### split_gps_trajectory_into_chunks

::: maggeo.parallel_processing.split_gps_trajectory_into_chunks
    options:
      show_root_heading: false

**Example:**

```python
# Split GPS trajectory into chunks
chunks = split_gps_trajectory_into_chunks(
    gps_df=large_gps_df,
    chunk_size=100
)
print(f"Created {len(chunks)} GPS chunks")
```

### process_gps_chunk_complete_pipeline

::: maggeo.parallel_processing.process_gps_chunk_complete_pipeline
    options:
      show_root_heading: false

## Processing Strategy

### Correct Parallel Architecture

Unlike typical parallel processing approaches, MagGeo uses a specialized strategy:

```python
gps_chunks = split_gps_trajectory_into_chunks(gps_df, chunk_size=100)

# Each worker gets:
# - Small GPS chunk (e.g., 100 points)
# - Complete Swarm data (A, B, C) for proper spatiotemporal matching
for gps_chunk in gps_chunks:
    result = process_chunk(gps_chunk, complete_swarm_a, complete_swarm_b, complete_swarm_c)
```

### Why This Architecture?

1. **Spatiotemporal Interpolation**: Each GPS point needs to find the best matches across ALL Swarm data
2. **Temporal Windows**: GPS points may need Swarm data from hours before/after
3. **Quality Filtering**: Workers need access to complete datasets to filter by quality
4. **Proper CHAOS Integration**: CHAOS calculations require complete interpolated datasets

## Performance Optimization

### Automatic Chunk Sizing

```python
# Automatic optimization based on data size and available cores
result = parallel_maggeo_annotation(
    gps_df=gps_df,
    swarm_a=swarm_a,
    swarm_b=swarm_b,
    swarm_c=swarm_c,
    # chunk_size automatically calculated
    # n_cores automatically detected
)
```

### Manual Tuning

```python
# Manual optimization for specific scenarios
optimal_chunk = get_optimal_chunk_size(
    total_gps_points=len(gps_df),
    n_cores=8,
    min_chunk_size=50  # Prevent tiny chunks
)

result = parallel_maggeo_annotation(
    gps_df=gps_df,
    swarm_a=swarm_a,
    swarm_b=swarm_b, 
    swarm_c=swarm_c,
    chunk_size=optimal_chunk,
    n_cores=8
)
```

## Integration with Main Workflow

### Automatic Parallel Processing

The main MagGeo function automatically uses parallel processing for large datasets:

```python
import maggeo

params = {
    'data_dir': 'data',
    'gpsfilename': 'large_trajectory.csv',  # 10,000+ points
    'lat_col': 'latitude',
    'long_col': 'longitude',
    'datetime_col': 'timestamp',
    'token': 'your_token',
    
    # Parallel processing enabled automatically for large datasets
    'parallel': True,  # Optional: force parallel processing
    'n_cores': 4       # Optional: specify core count
}

result = maggeo.annotate_gps_with_geomag(params)
```

## Complete Processing Pipeline

Each worker process follows this pipeline:

### 1. Interpolation Phase
```python
# For each GPS point in chunk:
# - Find spatiotemporally closest Swarm measurements using st_idw_process
# - Apply inverse distance weighting
# - Calculate interpolated magnetic field components
```

### 2. CHAOS Calculation Phase
```python
# For the complete chunk:
# - Calculate CHAOS model predictions using chaos_ground_values
# - Derive observed vs. model components
# - Add N, E, C, N_Obs, E_Obs, C_Obs columns
```

### 3. Component Derivation Phase
```python
# Calculate derived magnetic components:
# - H: Horizontal intensity = √(N² + E²)
# - D: Declination = arctan(E/N)
# - I: Inclination = arctan(C/H)  
# - F: Total intensity = √(N² + E² + C²)
```

## Error Handling

### Graceful Degradation

When a GPS point fails interpolation, the system creates a "bad point" result:

```python
bad_point_result = {
    'Latitude': gps_lat,
    'Longitude': gps_lon,
    'N_res': float('nan'),
    'E_res': float('nan'),
    'C_res': float('nan'),
    'TotalPoints': 0,
    'Minimum_Distance': float('nan'),
    'Average_Distance': float('nan'),
    'Kp': float('nan')
}
```

### CHAOS Calculation Failure

If CHAOS calculation fails for a chunk, NaN values are added for all CHAOS-derived columns: `N`, `E`, `C`, `N_Obs`, `E_Obs`, `C_Obs`, `H`, `D`, `I`, `F`.

## Performance Guidelines

**When to Use Parallel Processing:**
- GPS trajectories > 1,000 points: Significant speedup
- GPS trajectories > 10,000 points: Major performance improvement
- Multiple CPU cores available
- Sufficient RAM for complete Swarm datasets

**Performance Expectations:**

| GPS Points | Cores | Expected Speedup |
|------------|-------|------------------|
| 1,000      | 4     | 2-3x            |
| 10,000     | 4     | 3-4x            |
| 50,000     | 8     | 5-7x            |
| 100,000+   | 8     | 6-8x            |

*Actual performance depends on data complexity, system specifications, and Swarm data density.*