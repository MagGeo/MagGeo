# SwarmDataManager

::: maggeo.SwarmDataManager

## Overview

The `SwarmDataManager` is a class for efficient Swarm satellite data management in MagGeo. It provides persistent storage, resume capabilities, and intelligent data organization for research workflows.

## Key Features

- **Persistent Storage**: Download once, use many times
- **Resume Capability**: Continue interrupted downloads
- **Multiple Formats**: Parquet, CSV, and Pickle support
- **Automatic Organization**: Structured directory layout
- **Data Quality**: Built-in quality assessment and filtering
- **Memory Efficient**: Lazy loading and chunked processing

## Quick Start

```python
from maggeo import SwarmDataManager
import pandas as pd

# Create manager
manager = SwarmDataManager(
    data_dir="my_swarm_data",
    file_format="parquet"
)

# Load GPS trajectory
gps_df = pd.read_csv("trajectory.csv")
gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'])

# Download Swarm data
swarm_a, swarm_b, swarm_c = manager.download_for_trajectory(
    gps_df,
    token="your_vires_token"
)
```

## Directory Structure

The manager creates an organized directory structure:

```
my_swarm_data/
├── swarm_A/
│   ├── 2020/
│   │   ├── 01/
│   │   │   ├── swarm_A_2020-01-01.csv
│   │   │   └── swarm_A_2020-01-02.csv
│   │   └── 02/
│   └── concatenated/
│       └── swarm_A_2020-01-01_to_2020-01-31.csv
├── swarm_B/
├── swarm_C/
└── metadata/
    ├── download_log.json
    └── quality_reports.json
```

## Advanced Usage

### Custom Configuration

```python
manager = SwarmDataManager(
    data_dir="swarm_data",
    file_format="parquet",
    chunk_size=10000,
    parallel_download=True,
    quality_filter=True,
    compression="snappy"
)
```

### Batch Operations

```python
# Download for multiple trajectories
trajectories = ["traj1.csv", "traj2.csv", "traj3.csv"]

for traj_file in trajectories:
    gps_df = pd.read_csv(traj_file)
    manager.download_for_trajectory(gps_df, token=token)

# Load all data at once
all_data = manager.load_concatenated_data(
    satellites=['A', 'B', 'C'],
    start_date='2020-01-01',
    end_date='2020-12-31'
)
```

### Quality Control

```python
# Get quality report
quality_report = manager.get_quality_report('A')
print(f"Data coverage: {quality_report['coverage']:.2%}")
print(f"Missing points: {quality_report['missing_count']}")

# Filter by quality
high_quality_data = manager.load_concatenated_data(
    satellites=['A'],
    quality_threshold=0.9
)
```

## Performance Tips

!!! tip "Optimization Strategies"

    1. **Use Parquet format** for best performance
    2. **Enable parallel download** for large date ranges
    3. **Set appropriate chunk_size** based on available memory
    4. **Use concatenated files** for repeated analysis
    5. **Filter by quality** to reduce processing time

## Error Handling

The manager implements robust error handling:

```python
try:
    data = manager.download_for_trajectory(gps_df, token=token)
except SwarmDataError as e:
    print(f"Swarm data error: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except StorageError as e:
    print(f"Storage error: {e}")
```

## Integration with Core Functions

The manager seamlessly integrates with MagGeo's core functions:

```python
# Use with main annotation function
params = {
    'data_dir': 'gps_data',
    'gpsfilename': 'trajectory.csv',
    'use_swarm_manager': True,
    'swarm_data_dir': 'swarm_data',
    'swarm_manager_format': 'parquet',
    # ... other params
}

result = maggeo.annotate_gps_with_geomag(params)
```
