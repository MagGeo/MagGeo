# Geomagnetic Indices

The indices module provides functions to retrieve and integrate geomagnetic activity indices with GPS trajectory data.

::: maggeo.indices

## Overview

This module provides access to geomagnetic indices that characterize the state of Earth's magnetosphere:

- **AE Index**: Auroral Electrojet activity measure
- **SME Index**: SuperMAG Electrojet activity measure  
- **Integration**: Merge indices with GPS trajectory data

## Key Functions

### get_ae_index

::: maggeo.indices.get_ae_index
    options:
      show_root_heading: false

**Example:**

```python
from maggeo.indices import get_ae_index
import pandas as pd

# Get unique dates from GPS trajectory
gps_df = pd.read_csv('trajectory.csv')
gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'])
unique_dates = gps_df['timestamp'].dt.date.unique()

# Download AE index data
ae_data = get_ae_index(unique_dates, verbose=True)
print(f"Downloaded AE data: {len(ae_data)} records")
```

### get_sme_index

::: maggeo.indices.get_sme_index
    options:
      show_root_heading: false

**Example:**

```python
from maggeo.indices import get_sme_index

# Download SME index data
sme_data = get_sme_index(unique_dates, verbose=True)
print(f"Downloaded SME data: {len(sme_data)} records")
```

### merge_indices_with_maggeo

::: maggeo.indices.merge_indices_with_maggeo
    options:
      show_root_heading: false

**Example:**

```python
from maggeo.indices import merge_indices_with_maggeo

# Merge indices with GPS trajectory data
enhanced_df = merge_indices_with_maggeo(
    df_csv=gps_df,
    ae_data=ae_data,
    sme_data=sme_data,
    timestamp_col='timestamp'
)

# New columns: AE, SME indices interpolated to GPS timestamps
print(enhanced_df[['timestamp', 'latitude', 'longitude', 'AE', 'SME']].head())
```

## Available Indices

### AE Index (Auroral Electrojet)
- **Source**: Official geomagnetic observatories
- **Temporal Resolution**: 1 minute
- **Coverage**: Global auroral activity measure
- **Units**: nanoTesla (nT)
- **Range**: 0 to >2000 nT

### SME Index (SuperMAG Electrojet)
- **Source**: SuperMAG collaboration
- **Temporal Resolution**: 1 minute  
- **Coverage**: Enhanced global coverage
- **Units**: nanoTesla (nT)
- **Range**: 0 to >3000 nT

## Integration Workflow

### Complete Integration Example

```python
from maggeo.indices import get_ae_index, get_sme_index, merge_indices_with_maggeo
import pandas as pd

# 1. Load GPS trajectory
gps_df = pd.read_csv('bird_trajectory.csv')
gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'])

# 2. Get unique dates for index download
unique_dates = gps_df['timestamp'].dt.date.unique()
print(f"Downloading indices for {len(unique_dates)} unique dates")

# 3. Download geomagnetic indices
ae_data = get_ae_index(unique_dates, verbose=True)
sme_data = get_sme_index(unique_dates, verbose=True)

# 4. Merge with GPS data
enhanced_trajectory = merge_indices_with_maggeo(
    df_csv=gps_df,
    ae_data=ae_data,
    sme_data=sme_data,
    timestamp_col='timestamp'
)

# 5. Analyze results
print(f"AE range: {enhanced_trajectory['AE'].min():.0f} - {enhanced_trajectory['AE'].max():.0f} nT")
print(f"SME range: {enhanced_trajectory['SME'].min():.0f} - {enhanced_trajectory['SME'].max():.0f} nT")
```

## Activity Level Classification

### Using AE Index

```python
# Classify activity levels based on AE index
def classify_ae_activity(ae_value):
    if ae_value < 100:
        return 'quiet'
    elif ae_value < 300:
        return 'active'  
    elif ae_value < 500:
        return 'minor_storm'
    elif ae_value < 1000:
        return 'major_storm'
    else:
        return 'severe_storm'

enhanced_trajectory['activity_level'] = enhanced_trajectory['AE'].apply(classify_ae_activity)
```

### Activity Distribution

```python
# Analyze activity distribution
activity_counts = enhanced_trajectory['activity_level'].value_counts()
print("Activity level distribution:")
print(activity_counts)

# Filter for storm periods
storm_periods = enhanced_trajectory[
    enhanced_trajectory['activity_level'].str.contains('storm')
]
print(f"Storm periods: {len(storm_periods)} GPS points")
```

## Integration with Main MagGeo Workflow

### Automatic Index Integration

```python
import maggeo

# Indices are automatically included in main workflow
params = {
    'data_dir': 'data',
    'gpsfilename': 'trajectory.csv',
    'lat_col': 'latitude',
    'long_col': 'longitude',
    'datetime_col': 'timestamp',
    'token': 'your_vires_token',
    
    # Index integration settings
    'include_indices': True,  # Enable automatic index download
    'indices': ['AE', 'SME']  # Specify which indices to include
}

result = maggeo.annotate_gps_with_geomag(params)
# Result includes both magnetic field data AND geomagnetic indices
```

## Data Quality and Availability

### Data Coverage

- **AE Index**: Available from 1957 to present
- **SME Index**: Available from 1970 to present
- **Real-time availability**: ~1-2 hours delay
- **Definitive data**: ~1 month delay

### Quality Considerations

```python
# Check for missing data
missing_ae = enhanced_trajectory['AE'].isna().sum()
missing_sme = enhanced_trajectory['SME'].isna().sum()

print(f"Missing AE data: {missing_ae} points")
print(f"Missing SME data: {missing_sme} points")

# Handle missing data
enhanced_trajectory['AE'].fillna(method='ffill', inplace=True)  # Forward fill
enhanced_trajectory['SME'].fillna(method='interpolate', inplace=True)  # Interpolate
```

## Error Handling

### Network Issues

```python
try:
    ae_data = get_ae_index(unique_dates, verbose=True)
except Exception as e:
    print(f"Failed to download AE data: {e}")
    ae_data = None  # Continue without AE data

try:
    sme_data = get_sme_index(unique_dates, verbose=True)
except Exception as e:
    print(f"Failed to download SME data: {e}")
    sme_data = None  # Continue without SME data
```

### Graceful Degradation

```python
# Merge with available indices only
enhanced_trajectory = merge_indices_with_maggeo(
    df_csv=gps_df,
    ae_data=ae_data if ae_data is not None else None,
    sme_data=sme_data if sme_data is not None else None,
    timestamp_col='timestamp'
)

# Check which indices were successfully added
available_indices = []
if 'AE' in enhanced_trajectory.columns:
    available_indices.append('AE')
if 'SME' in enhanced_trajectory.columns:
    available_indices.append('SME')
    
print(f"Successfully integrated indices: {available_indices}")
```
