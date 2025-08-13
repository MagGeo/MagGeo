# API Reference

MagGeo provides a comprehensive API for geomagnetic field analysis and GPS trajectory annotation.

# API Reference

## Core Functions

::: maggeo.annotate_gps_with_geomag

## SwarmDataManager

::: maggeo.SwarmDataManager

### Methods

::: maggeo.SwarmDataManager.download_for_trajectory

::: maggeo.SwarmDataManager.load_concatenated_data

## Utility Functions

::: maggeo.download_swarm_data_for_trajectory

::: maggeo.load_swarm_data


## Quick Reference

### Core Functions

| Function | Description |
|----------|-------------|
| [`annotate_gps_with_geomag`](core.md#annotate_gps_with_geomag) | Main function for annotating GPS trajectories |
| [`download_swarm_data_for_trajectory`](core.md#download_swarm_data_for_trajectory) | Download Swarm data for specific trajectory |
| [`load_swarm_data`](core.md#load_swarm_data) | Load previously downloaded Swarm data |

### Classes

| Class | Description |
|-------|-------------|
| [`SwarmDataManager`](swarm_data_manager.md) | Manages Swarm data downloading and storage |

### Modules

| Module | Description |
|--------|-------------|
| [`parallel_processing`](parallel_processing.md) | Parallel processing utilities |
| [`indices`](indices.md) | Geomagnetic indices and calculations |

## Architecture Overview

```
GPS Trajectory → MagGeo Core → SwarmDataManager → VirES API
     ↓              ↓              ↓
Input Data → Processing Pipeline → Local Storage
     ↓              ↓              ↓
Validation → Interpolation → Persistent Files
     ↓              ↓              ↓
Quality Check → CHAOS Model → Annotated Output
```

## Data Flow

1. **Input**: GPS trajectory with coordinates and timestamps
2. **Data Acquisition**: Download Swarm satellite data via VirES API
3. **Storage**: Persist data locally for reuse (SwarmDataManager)
4. **Processing**: Interpolate magnetic field values to GPS locations
5. **Enhancement**: Add CHAOS model data and geomagnetic indices
6. **Output**: Annotated trajectory with comprehensive magnetic field information


## Performance Considerations

- **Use SwarmDataManager** for repeated analysis of the same time periods
- **Enable parallel processing** for large datasets (>10,000 GPS points)
- **Choose appropriate file formats**: Parquet for performance, CSV for compatibility
- **Batch process** multiple trajectories when possible

## Error Handling

All MagGeo functions implement comprehensive error handling, you need to activate the DEBUG mode to see the error messages. Use the `--debug` flag when running scripts or set the environment variable `MAGGEO_DEBUG=1`.

```bash
MAGGEO_DEBUG=1 python -m maggeo.annotate_gps_with_geomag --debug
```
