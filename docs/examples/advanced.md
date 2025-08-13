# Advanced Workflows

This page demonstrates advanced MagGeo workflows for complex geomagnetic analysis scenarios.

## Large-Scale Trajectory Analysis

### Parallel Processing for Big Data

```python
import maggeo
from maggeo.parallel_processing import parallel_maggeo_annotation
import pandas as pd

# Load large GPS trajectory (100,000+ points)
large_gps_df = pd.read_csv('massive_trajectory.csv')
large_gps_df['timestamp'] = pd.to_datetime(large_gps_df['timestamp'])

# Download Swarm data first
swarm_a, swarm_b, swarm_c = maggeo.download_swarm_data_for_trajectory(
    large_gps_df, token='your_vires_token'
)

# Process in parallel (much faster for large datasets)
result = parallel_maggeo_annotation(
    gps_df=large_gps_df,
    swarm_a=swarm_a,
    swarm_b=swarm_b,
    swarm_c=swarm_c,
    dt_seconds=14400,  # 4-hour time window
    n_cores=4,         # Use 4 CPU cores
    chunk_size=1000    # Process 1000 points per chunk
)

print(f"🚀 Processed {len(result)} GPS points using parallel processing")
```

### Memory-Efficient Processing

```python
from maggeo import SwarmDataManager

# Setup manager for large datasets
manager = SwarmDataManager(
    data_dir="large_swarm_data",
    file_format="parquet",  # Most efficient format
    chunk_size=5000        # Smaller chunks for memory efficiency
)

# Process large trajectory in chunks
def process_large_trajectory(gps_file, token, chunk_size=10000):
    """Process large GPS trajectory efficiently."""
    
    # Read GPS data in chunks
    gps_chunks = pd.read_csv(gps_file, chunksize=chunk_size)
    
    all_results = []
    
    for i, gps_chunk in enumerate(gps_chunks):
        print(f"Processing chunk {i+1}...")
        
        # Ensure datetime format
        gps_chunk['timestamp'] = pd.to_datetime(gps_chunk['timestamp'])
        
        # Download Swarm data for this chunk
        swarm_data = manager.download_for_trajectory(gps_chunk, token=token)
        
        # Annotate chunk
        chunk_result = maggeo.annotate_gps_with_geomag({
            'gps_data': gps_chunk,
            'swarm_data': swarm_data,
            'token': token
        })
        
        all_results.append(chunk_result)
    
    # Combine all results
    final_result = pd.concat(all_results, ignore_index=True)
    return final_result

# Process massive file
result = process_large_trajectory('massive_trajectory.csv', 'your_token')
```

## Multi-Trajectory Comparative Analysis

### Compare Multiple Animals/Tracks

```python
import matplotlib.pyplot as plt
import numpy as np

def compare_multiple_trajectories(trajectory_files, token):
    """Compare magnetic field exposure across multiple trajectories."""
    
    results = {}
    
    for traj_file in trajectory_files:
        print(f"Processing {traj_file}...")
        
        # Process each trajectory
        params = {
            'data_dir': 'data',
            'gpsfilename': traj_file,
            'lat_col': 'latitude',
            'long_col': 'longitude',
            'datetime_col': 'timestamp',
            'token': token
        }
        
        result = maggeo.annotate_gps_with_geomag(params)
        
        # Extract trajectory name
        traj_name = traj_file.replace('.csv', '').replace('_trajectory', '')
        results[traj_name] = result
    
    # Comparative analysis
    print("\n📊 Comparative Analysis:")
    
    for name, data in results.items():
        f_mean = data['F'].mean()
        f_std = data['F'].std()
        kp_mean = data['Kp'].mean()
        
        print(f"{name}:")
        print(f"  Average F: {f_mean:.1f} ± {f_std:.1f} nT")
        print(f"  Average Kp: {kp_mean:.2f}")
        print(f"  Points: {len(data)}")
    
    # Plot comparison
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Magnetic field intensity comparison
    for name, data in results.items():
        ax1.plot(data['timestamp'], data['F'], label=name, alpha=0.7)
    
    ax1.set_title('Magnetic Field Intensity Comparison')
    ax1.set_ylabel('F (nT)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Kp index comparison
    for name, data in results.items():
        ax2.plot(data['timestamp'], data['Kp'], label=name, alpha=0.7)
    
    ax2.set_title('Geomagnetic Activity Comparison')
    ax2.set_ylabel('Kp Index')
    ax2.set_xlabel('Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return results

# Compare multiple trajectories
trajectory_files = ['bird_A.csv', 'bird_B.csv', 'bird_C.csv']
comparison_results = compare_multiple_trajectories(trajectory_files, 'your_token')
```

## Temporal Analysis

### Magnetic Storm Impact Analysis

```python
def analyze_storm_impact(result):
    """Analyze how geomagnetic storms affect magnetic field measurements."""
    
    # Classify activity levels
    result['activity_level'] = pd.cut(
        result['Kp'], 
        bins=[0, 3, 5, 7, 9], 
        labels=['Quiet', 'Active', 'Storm', 'Severe']
    )
    
    # Calculate residuals (observed - model)
    result['F_residual'] = result['F'] - result['F'].rolling(window=10).mean()
    result['N_residual'] = result['N_Obs'] - result['N']
    result['E_residual'] = result['E_Obs'] - result['E']
    result['C_residual'] = result['C_Obs'] - result['C']
    
    # Analysis by activity level
    storm_analysis = result.groupby('activity_level').agg({
        'F': ['mean', 'std'],
        'F_residual': ['mean', 'std'],
        'N_residual': ['mean', 'std'],
        'E_residual': ['mean', 'std'],
        'C_residual': ['mean', 'std']
    }).round(2)
    
    print("🌩️ Storm Impact Analysis:")
    print(storm_analysis)
    
    # Plot storm effects
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Total field vs Kp
    scatter = axes[0,0].scatter(result['Kp'], result['F'], 
                               c=result['Kp'], cmap='plasma', alpha=0.6)
    axes[0,0].set_xlabel('Kp Index')
    axes[0,0].set_ylabel('Total Field F (nT)')
    axes[0,0].set_title('Magnetic Field vs Geomagnetic Activity')
    plt.colorbar(scatter, ax=axes[0,0])
    
    # Residuals vs Kp
    axes[0,1].scatter(result['Kp'], result['F_residual'], alpha=0.6)
    axes[0,1].set_xlabel('Kp Index')
    axes[0,1].set_ylabel('F Residual (nT)')
    axes[0,1].set_title('Field Residuals vs Activity')
    axes[0,1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
    
    # Component residuals
    components = ['N_residual', 'E_residual', 'C_residual']
    colors = ['red', 'green', 'blue']
    
    for comp, color in zip(components, colors):
        axes[1,0].scatter(result['Kp'], result[comp], 
                         alpha=0.6, label=comp.replace('_residual', ''), 
                         color=color, s=10)
    
    axes[1,0].set_xlabel('Kp Index')
    axes[1,0].set_ylabel('Component Residuals (nT)')
    axes[1,0].set_title('Component Residuals vs Activity')
    axes[1,0].legend()
    axes[1,0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # Time series of storm periods
    storm_periods = result[result['Kp'] >= 5]  # Storm conditions
    
    axes[1,1].plot(result['timestamp'], result['F'], 'b-', alpha=0.3, label='All data')
    if len(storm_periods) > 0:
        axes[1,1].scatter(storm_periods['timestamp'], storm_periods['F'], 
                         color='red', s=20, label='Storm periods', zorder=5)
    
    axes[1,1].set_xlabel('Time')
    axes[1,1].set_ylabel('Total Field F (nT)')
    axes[1,1].set_title('Storm Periods Highlighted')
    axes[1,1].legend()
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    return storm_analysis

# Run storm analysis
storm_results = analyze_storm_impact(result)
```

## Spatial Analysis

### Magnetic Anomaly Detection

```python
def detect_magnetic_anomalies(result, threshold_std=2.5):
    """Detect spatial magnetic anomalies along trajectory."""
    
    # Calculate moving statistics
    window_size = min(50, len(result) // 10)  # Adaptive window size
    
    result['F_smooth'] = result['F'].rolling(window=window_size, center=True).mean()
    result['F_std'] = result['F'].rolling(window=window_size, center=True).std()
    
    # Detect anomalies
    result['F_anomaly'] = abs(result['F'] - result['F_smooth']) > (threshold_std * result['F_std'])
    
    # Spatial clustering of anomalies
    anomalies = result[result['F_anomaly'] == True].copy()
    
    if len(anomalies) > 0:
        print(f"🔍 Detected {len(anomalies)} magnetic anomalies")
        print(f"Anomaly locations:")
        
        for idx, anomaly in anomalies.iterrows():
            lat, lon = anomaly['location-lat'], anomaly['location-long']
            f_val = anomaly['F']
            deviation = abs(anomaly['F'] - anomaly['F_smooth'])
            
            print(f"  {lat:.4f}°N, {lon:.4f}°E: F={f_val:.1f} nT (±{deviation:.1f} nT)")
    
    # Plot anomalies
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Trajectory map with anomalies
    ax1.plot(result['location-long'], result['location-lat'], 'b-', alpha=0.6, linewidth=1)
    
    if len(anomalies) > 0:
        scatter = ax1.scatter(anomalies['location-long'], anomalies['location-lat'], 
                             c=anomalies['F'], cmap='coolwarm', s=50, 
                             edgecolors='black', linewidth=1, zorder=5)
        plt.colorbar(scatter, ax=ax1, label='F (nT)')
    
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.set_title('Trajectory with Magnetic Anomalies')
    ax1.grid(True, alpha=0.3)
    
    # Time series with anomalies highlighted
    ax2.plot(result['timestamp'], result['F'], 'b-', alpha=0.6, label='F observed')
    ax2.plot(result['timestamp'], result['F_smooth'], 'g-', alpha=0.8, label='F smoothed')
    
    if len(anomalies) > 0:
        ax2.scatter(anomalies['timestamp'], anomalies['F'], 
                   color='red', s=30, label='Anomalies', zorder=5)
    
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Magnetic Field F (nT)')
    ax2.set_title('Magnetic Field with Anomaly Detection')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    return anomalies

# Detect anomalies
anomalies = detect_magnetic_anomalies(result, threshold_std=2.5)
```

## Integration with Geomagnetic Indices

### Complete Geomagnetic Context

```python
from maggeo.indices import get_ae_index, get_sme_index, merge_indices_with_maggeo

def comprehensive_analysis(gps_file, token):
    """Complete analysis with all geomagnetic context."""
    
    # Step 1: Load and process GPS trajectory
    gps_df = pd.read_csv(gps_file)
    gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'])
    
    params = {
        'data_dir': 'data',
        'gpsfilename': gps_file,
        'lat_col': 'latitude',
        'long_col': 'longitude',
        'datetime_col': 'timestamp',
        'token': token
    }
    
    # Get magnetic field annotation
    result = maggeo.annotate_gps_with_geomag(params)
    
    # Step 2: Add geomagnetic indices
    unique_dates = result['timestamp'].dt.date.unique()
    
    try:
        ae_data = get_ae_index(unique_dates, verbose=True)
        sme_data = get_sme_index(unique_dates, verbose=True)
        
        # Merge indices
        result = merge_indices_with_maggeo(
            result, ae_data=ae_data, sme_data=sme_data, 
            timestamp_col='timestamp'
        )
        
        print("✅ Added AE and SME indices")
        
    except Exception as e:
        print(f"⚠️ Could not download indices: {e}")
    
    # Step 3: Comprehensive analysis
    print("\n📊 Comprehensive Geomagnetic Analysis:")
    
    # Basic statistics
    print(f"Trajectory duration: {result['timestamp'].min()} to {result['timestamp'].max()}")
    print(f"Total points: {len(result)}")
    print(f"Magnetic field range: {result['F'].min():.1f} - {result['F'].max():.1f} nT")
    print(f"Kp range: {result['Kp'].min():.1f} - {result['Kp'].max():.1f}")
    
    if 'AE' in result.columns:
        print(f"AE range: {result['AE'].min():.0f} - {result['AE'].max():.0f} nT")
    
    if 'SME' in result.columns:
        print(f"SME range: {result['SME'].min():.0f} - {result['SME'].max():.0f} nT")
    
    # Activity classification
    result['activity_class'] = 'Quiet'
    result.loc[result['Kp'] >= 4, 'activity_class'] = 'Active'
    result.loc[result['Kp'] >= 6, 'activity_class'] = 'Storm'
    
    activity_dist = result['activity_class'].value_counts()
    print(f"\nActivity distribution:")
    for activity, count in activity_dist.items():
        pct = count / len(result) * 100
        print(f"  {activity}: {count} points ({pct:.1f}%)")
    
    # Comprehensive plotting
    fig, axes = plt.subplots(3, 1, figsize=(15, 12))
    
    # Magnetic field components
    axes[0].plot(result['timestamp'], result['F'], 'b-', label='Total F', alpha=0.8)
    axes[0].plot(result['timestamp'], result['H'], 'g-', label='Horizontal H', alpha=0.8)
    axes[0].set_ylabel('Magnetic Field (nT)')
    axes[0].set_title('Magnetic Field Components')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Geomagnetic activity
    axes[1].plot(result['timestamp'], result['Kp'], 'r-', label='Kp index', linewidth=2)
    if 'AE' in result.columns:
        ax1_twin = axes[1].twinx()
        ax1_twin.plot(result['timestamp'], result['AE'], 'orange', alpha=0.7, label='AE index')
        ax1_twin.set_ylabel('AE Index (nT)', color='orange')
    
    axes[1].set_ylabel('Kp Index')
    axes[1].set_title('Geomagnetic Activity Indices')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Magnetic declination and inclination
    axes[2].plot(result['timestamp'], result['D'], 'purple', label='Declination', alpha=0.8)
    ax2_twin = axes[2].twinx()
    ax2_twin.plot(result['timestamp'], result['I'], 'brown', alpha=0.8, label='Inclination')
    ax2_twin.set_ylabel('Inclination (°)', color='brown')
    
    axes[2].set_ylabel('Declination (°)', color='purple')
    axes[2].set_xlabel('Time')
    axes[2].set_title('Magnetic Field Direction')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return result

# Run comprehensive analysis
comprehensive_result = comprehensive_analysis('trajectory.csv', 'your_token')
```

## Export and Reporting

### Generate Analysis Report

```python
def generate_analysis_report(result, output_file='magnetic_analysis_report.html'):
    """Generate comprehensive HTML report."""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MagGeo Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; }}
            .stats {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧭 MagGeo Analysis Report</h1>
            <p>Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>📊 Trajectory Summary</h2>
            <div class="stats">
                <p><strong>Total GPS Points:</strong> {len(result):,}</p>
                <p><strong>Time Period:</strong> {result['timestamp'].min()} to {result['timestamp'].max()}</p>
                <p><strong>Duration:</strong> {(result['timestamp'].max() - result['timestamp'].min()).days} days</p>
                <p><strong>Average Distance:</strong> {result['Average_Distance'].iloc[0]:.1f} meters</p>
            </div>
        </div>
        
        <div class="section">
            <h2>🧲 Magnetic Field Statistics</h2>
            <table>
                <tr><th>Component</th><th>Mean (nT)</th><th>Std (nT)</th><th>Min (nT)</th><th>Max (nT)</th></tr>
                <tr><td>Total Field (F)</td><td>{result['F'].mean():.1f}</td><td>{result['F'].std():.1f}</td><td>{result['F'].min():.1f}</td><td>{result['F'].max():.1f}</td></tr>
                <tr><td>North (N)</td><td>{result['N'].mean():.1f}</td><td>{result['N'].std():.1f}</td><td>{result['N'].min():.1f}</td><td>{result['N'].max():.1f}</td></tr>
                <tr><td>East (E)</td><td>{result['E'].mean():.1f}</td><td>{result['E'].std():.1f}</td><td>{result['E'].min():.1f}</td><td>{result['E'].max():.1f}</td></tr>
                <tr><td>Center (C)</td><td>{result['C'].mean():.1f}</td><td>{result['C'].std():.1f}</td><td>{result['C'].min():.1f}</td><td>{result['C'].max():.1f}</td></tr>
                <tr><td>Horizontal (H)</td><td>{result['H'].mean():.1f}</td><td>{result['H'].std():.1f}</td><td>{result['H'].min():.1f}</td><td>{result['H'].max():.1f}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>🌩️ Geomagnetic Activity</h2>
            <div class="stats">
                <p><strong>Average Kp:</strong> {result['Kp'].mean():.2f}</p>
                <p><strong>Max Kp:</strong> {result['Kp'].max():.1f}</p>
                <p><strong>Activity Level:</strong> {'Quiet' if result['Kp'].mean() < 3 else 'Active' if result['Kp'].mean() < 5 else 'Disturbed'}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Data Quality</h2>
            <div class="stats">
                <p><strong>Complete F measurements:</strong> {(~result['F'].isna()).sum():,} / {len(result):,} ({(~result['F'].isna()).sum()/len(result)*100:.1f}%)</p>
                <p><strong>Complete Kp values:</strong> {(~result['Kp'].isna()).sum():,} / {len(result):,} ({(~result['Kp'].isna()).sum()/len(result)*100:.1f}%)</p>
            </div>
        </div>
        
        <div class="section">
            <h2>💾 Data Files</h2>
            <p>Annotated trajectory saved as: <code>{output_file.replace('.html', '.csv')}</code></p>
        </div>
        
        <div class="section">
            <h2>🔧 Analysis Settings</h2>
            <div class="stats">
                <p><strong>MagGeo Version:</strong> v0.2.0</p>
                <p><strong>Processing Method:</strong> Swarm satellite data + CHAOS model</p>
                <p><strong>Coordinate System:</strong> NEC (North-East-Center)</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save HTML report
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    # Save CSV data
    csv_file = output_file.replace('.html', '.csv')
    result.to_csv(csv_file, index=False)
    
    print(f"📄 Analysis report saved: {output_file}")
    print(f"💾 Data saved: {csv_file}")

# Generate report
generate_analysis_report(result, 'my_trajectory_analysis.html')
```

## Next Steps

- **API Documentation**: See [API Reference](../api/index.md) for detailed function documentation
- **Performance**: Check [Parallel Processing](../api/parallel_processing.md) for optimization tips
- **Basic Examples**: Return to [Basic Examples](basic.md) for simpler workflows
