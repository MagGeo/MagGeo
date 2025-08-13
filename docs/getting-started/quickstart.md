# Quick Start

Running MagGeo in just a few minutes!

## 1. Prepare Your Data

MagGeo works with GPS trajectory data in CSV format:

```csv
timestamp,latitude,longitude, altitude
2020-01-01 12:00:00,-45.123,123.456,0
2020-01-01 12:01:00,-45.124,123.457,0.46
2020-01-01 12:02:00,-45.125,123.458,0.92
```

## 2. Basic Usage

### Method 1: Simple Function Call

```python
import maggeo

# Configure parameters
params = {
    'data_dir': 'data',
    'gpsfilename': 'my_trajectory.csv',
    'lat_col': 'latitude',
    'long_col': 'longitude',
    'datetime_col': 'timestamp',
    'token': 'your_vires_token_here'
}

# Annotate trajectory with geomagnetic data
result = maggeo.annotate_gps_with_geomag(params)
print(f"✅ Processed {len(result)} GPS points")
```

### Method 2: SwarmDataManager (Recommended)

For better performance and data reuse:

```python
from maggeo import SwarmDataManager

# Create manager with persistent storage
manager = SwarmDataManager(
    data_dir="swarm_data",
    file_format="csv"  # or 'parquet'
)

# Load your GPS data
import pandas as pd
gps_df = pd.read_csv('my_trajectory.csv')
gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'])

# Download Swarm data (only once!)
swarm_a, swarm_b, swarm_c = manager.download_for_trajectory(
    gps_df, 
    token='your_vires_token_here'
)

# Next time, just load from storage (much faster!)
data = manager.load_concatenated_data(['A', 'B', 'C'])
```

## 3. Command Line Interface

MagGeo also provides a CLI for batch processing:

```bash
# Create a configuration file
cat > config.yml << EOF
data_dir: "data"
gpsfilename: "trajectory.csv"
lat_col: "latitude"
long_col: "longitude"
datetime_col: "timestamp"
use_swarm_manager: true
swarm_data_dir: "swarm_data"
EOF

# Run annotation
maggeo annotate --config config.yml --token YOUR_TOKEN
```

## 4. Explore Your Results

The annotated data includes rich geomagnetic information:

```python
# Examine the results
print(result.columns)

# Plot magnetic field intensity
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(result['timestamp'], result['F'])
plt.title('Magnetic Field Intensity Along Trajectory')
plt.xlabel('Time')
plt.ylabel('Magnetic Field Intensity (nT)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

## 5. Parallel Processing

For large datasets, enable parallel processing:

```python
params['parallel'] = True
params['n_cores'] = 4  # Use 4 CPU cores
result = maggeo.annotate_gps_with_geomag(params)
```
## 6. Documentation and Help
For more details, check the [MagGeo Documentation](https://maggeo.github.io/MagGeo/).

## 7. Troubleshooting
If you encounter issues:
- Ensure your CSV has the correct column names
- Check your ViRES token is valid
- Review the logs for any errors during processing
  