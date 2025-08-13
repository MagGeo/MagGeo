# Basic Examples

This page provides simple, practical examples of using MagGeo for common geomagnetic analysis tasks.

## Basic GPS Trajectory Annotation

### Simple Annotation

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

# Annotate trajectory with magnetic field data
result = maggeo.annotate_gps_with_geomag(params)
print(f"✅ Annotated {len(result)} GPS points with magnetic field data")
```

### Expected Output

The result contains your GPS data plus magnetic field information:

```python
print(result.columns.tolist())
# ['timestamp', 'location-long', 'location-lat', 'height', 'individual_id',
#  'TotalPoints', 'Minimum_Distance', 'Average_Distance', 'Kp',
#  'N', 'E', 'C', 'N_Obs', 'E_Obs', 'C_Obs', 'H', 'D', 'I', 'F']

# View sample data
print(result.head())
```

## Using SwarmDataManager for Persistent Storage

### Basic Setup

```python
from maggeo import SwarmDataManager
import pandas as pd

# Create manager for persistent storage
manager = SwarmDataManager(
    data_dir="my_swarm_data",
    file_format="parquet"  # Recommended for performance
)

# Load GPS trajectory
gps_df = pd.read_csv('trajectory.csv')
gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'])

# Download Swarm data (only once!)
swarm_a, swarm_b, swarm_c = manager.download_for_trajectory(
    gps_df, 
    token='your_vires_token'
)

print(f"📊 Downloaded Swarm data:")
print(f"   Swarm A: {len(swarm_a)} records")
print(f"   Swarm B: {len(swarm_b)} records") 
print(f"   Swarm C: {len(swarm_c)} records")
```

### Reuse Downloaded Data

```python
# Next time, load instantly from storage
data = manager.load_concatenated_data(['A', 'B', 'C'])
print(f"⚡ Loaded {len(data)} records from storage (much faster!)")
```

## Working with Different Data Formats

### CSV Input/Output

```python
import pandas as pd

# Read GPS data from CSV
gps_df = pd.read_csv('bird_trajectory.csv')

# Ensure datetime column is properly formatted
gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'])

# Process with MagGeo
params = {
    'data_dir': 'data',
    'gpsfilename': 'bird_trajectory.csv',
    'lat_col': 'lat',      # Adjust column names as needed
    'long_col': 'lon',
    'datetime_col': 'timestamp',
    'token': 'your_vires_token'
}

result = maggeo.annotate_gps_with_geomag(params)

# Save results
result.to_csv('annotated_trajectory.csv', index=False)
print("💾 Results saved to annotated_trajectory.csv")
```

## Analyzing Magnetic Field Components

### Plot Magnetic Field Intensity

```python
import matplotlib.pyplot as plt
import pandas as pd

# After annotation
result = maggeo.annotate_gps_with_geomag(params)

# Plot total magnetic field intensity
plt.figure(figsize=(12, 6))
plt.plot(result['timestamp'], result['F'], 'b-', linewidth=1)
plt.title('Total Magnetic Field Intensity Along Trajectory')
plt.xlabel('Time')
plt.ylabel('Magnetic Field Intensity (nT)')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### Compare Model vs Observations

```python
# Plot model vs observed values
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

components = [('N', 'N_Obs'), ('E', 'E_Obs'), ('C', 'C_Obs')]
titles = ['North Component', 'East Component', 'Center Component']

for i, ((model, obs), title) in enumerate(zip(components, titles)):
    axes[i].plot(result['timestamp'], result[model], 'b-', label='CHAOS Model', alpha=0.7)
    axes[i].plot(result['timestamp'], result[obs], 'r-', label='Swarm Observed', alpha=0.7)
    axes[i].set_title(title)
    axes[i].set_ylabel('Magnetic Field (nT)')
    axes[i].legend()
    axes[i].grid(True, alpha=0.3)

plt.xlabel('Time')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

## Error Handling

### Robust Processing

```python
import maggeo

def safe_annotation(params):
    """Safely annotate GPS trajectory with error handling."""
    try:
        result = maggeo.annotate_gps_with_geomag(params)
        print(f"✅ Successfully processed {len(result)} GPS points")
        return result
        
    except FileNotFoundError:
        print("❌ GPS file not found. Check file path and name.")
        return None
        
    except ConnectionError:
        print("❌ Network error. Check internet connection and VirES token.")
        return None
        
    except ValueError as e:
        print(f"❌ Data validation error: {e}")
        print("Check column names and data format.")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

# Use safe processing
result = safe_annotation(params)
if result is not None:
    # Continue with analysis
    print("Data ready for analysis!")
```

## Quality Assessment

### Check Data Quality

```python
# After annotation, assess data quality
def assess_quality(result):
    """Assess quality of annotated GPS data."""
    
    print("📊 Data Quality Assessment:")
    print(f"   Total GPS points: {len(result)}")
    
    # Check for missing magnetic field data
    missing_f = result['F'].isna().sum()
    print(f"   Missing F values: {missing_f} ({missing_f/len(result)*100:.1f}%)")
    
    # Check magnetic field range
    f_min, f_max = result['F'].min(), result['F'].max()
    print(f"   F range: {f_min:.0f} - {f_max:.0f} nT")
    
    # Check for extreme values (potential outliers)
    f_mean, f_std = result['F'].mean(), result['F'].std()
    outliers = result[abs(result['F'] - f_mean) > 3 * f_std]
    print(f"   Potential outliers: {len(outliers)} points")
    
    # Check geomagnetic activity level
    kp_mean = result['Kp'].mean()
    print(f"   Average Kp: {kp_mean:.1f}")
    
    if kp_mean < 3:
        print("   🟢 Quiet geomagnetic conditions")
    elif kp_mean < 5:
        print("   🟡 Active geomagnetic conditions")
    else:
        print("   🔴 Disturbed geomagnetic conditions")

# Assess quality
assess_quality(result)
```

## Batch Processing

### Process Multiple Files

```python
import os
import glob

def process_multiple_trajectories(data_dir, token):
    """Process all CSV files in a directory."""
    
    # Find all CSV files
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    print(f"Found {len(csv_files)} CSV files to process")
    
    results = {}
    
    for csv_file in csv_files:
        print(f"\n🔄 Processing {os.path.basename(csv_file)}...")
        
        # Setup parameters
        params = {
            'data_dir': data_dir,
            'gpsfilename': os.path.basename(csv_file),
            'lat_col': 'latitude',
            'long_col': 'longitude',
            'datetime_col': 'timestamp',
            'token': token
        }
        
        # Process file
        result = maggeo.annotate_gps_with_geomag(params)
        
        if result is not None:
            # Save result
            output_name = csv_file.replace('.csv', '_annotated.csv')
            result.to_csv(output_name, index=False)
            results[csv_file] = len(result)
            print(f"✅ Saved {len(result)} annotated points to {output_name}")
        else:
            print(f"❌ Failed to process {csv_file}")
    
    # Summary
    print(f"\n📋 Processing Summary:")
    for file, points in results.items():
        print(f"   {os.path.basename(file)}: {points} points")
    
    return results

# Process all trajectories
results = process_multiple_trajectories('data/trajectories', 'your_vires_token')
```

## Common Issues and Solutions

### Issue: Column Name Mismatch

```python
# Check your GPS file columns
gps_df = pd.read_csv('your_file.csv')
print("Available columns:", gps_df.columns.tolist())

# Common column name variations
column_mapping = {
    'lat': 'latitude',
    'lon': 'longitude', 
    'long': 'longitude',
    'time': 'timestamp',
    'datetime': 'timestamp',
    'date_time': 'timestamp'
}

# Rename columns if needed
gps_df.rename(columns=column_mapping, inplace=True)
```

### Issue: DateTime Format Problems

```python
# Handle different datetime formats
import pandas as pd

# Try automatic parsing first
gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'])

# If that fails, specify format explicitly
gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'], format='%Y-%m-%d %H:%M:%S')

# For other formats
gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'], format='%d/%m/%Y %H:%M')
```

### Issue: Large File Processing

```python
# For large GPS files, use parallel processing
params = {
    'data_dir': 'data',
    'gpsfilename': 'large_trajectory.csv',  # 10,000+ points
    'lat_col': 'latitude',
    'long_col': 'longitude',
    'datetime_col': 'timestamp',
    'token': 'your_vires_token',
    
    # Enable parallel processing
    'parallel': True,
    'n_cores': 4  # Use 4 CPU cores
}

result = maggeo.annotate_gps_with_geomag(params)
```

## Next Steps

- **Advanced Workflows**: See [Advanced Examples](advanced.md) for complex analysis patterns
- **API Reference**: Check [Core Functions](../api/core.md) for detailed function documentation
- **User Guide**: Read [Basic Usage](../user-guide/basic-usage.md) for comprehensive guidance
