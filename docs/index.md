# MagGeo: Library to annotate GPS trajectories with Geomagnetic data from Swarm satellites

<div align="center">
  <img src="https://img.shields.io/pypi/v/maggeo?style=flat-square" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/maggeo?style=flat-square" alt="Python">
  <img src="https://img.shields.io/github/license/fbenitez92/maggeo?style=flat-square" alt="License">
  <img src="https://img.shields.io/github/stars/fbenitez92/maggeo?style=flat-square" alt="Stars">
</div>

MagGeo is a Python package for annotating GPS trajectories with geomagnetic field data from the European Space Agency's **Swarm satellite constellation**. Developed and  designed for movement ecology research, MagGeo provides researchers with the tools to incorporate Earth's magnetic field information into their GPS trajectories and allow to run several spatial-temporal analysis related to the the animal movement.

The concepts and the methods developed in MagGeo are based on the work of Benitez-Paez, F., Brum-Bastos, V.d., Beggan, C.D. et al. Fusion of wildlife tracking and satellite geomagnetic data for the study of animal migration. Mov Ecol 9, 31 (2021). https://doi.org/10.1186/s40462-021-00268-4

## Key Features

!!! success "What makes MagGeo Useful?"
    - **🌐 ESA Swarm Data**: Direct access to high-quality geomagnetic data from ESA's Swarm satellites
    - **📈 Easy Annotation**: Simple API for annotating GPS trajectories with geomagnetic
    - **💾 Smart Data Management**: Persistent storage with resume capabilities for large datasets
    - **⚡ Parallel Processing**: Efficient handling of massive GPS trajectories
    - **🔧 Flexible Interface**: Both programmatic Python API and command-line tools
  
## Quick Start

MagGeo is developed using Python. To get started with MagGeo in just a few lines of code:

```python
import maggeo

# Basic trajectory annotation
params = {
    'data_dir': 'data/sample_data',
    'gpsfilename': 'BirdGPSTrajectory.csv',
    'lat_col': 'latitude',
    'long_col': 'longitude', 
    'datetime_col': 'timestamp',
    'token': 'your_vires_token'
}

# Annotate your GPS trajectory with geomagnetic data
result = maggeo.annotate_gps_with_geomag(params)
``` 
!!! tip "New in v0.2.0:"

    ```python
    # Use SwarmDataManager for reusable data storage
    from maggeo import SwarmDataManager
    
    manager = SwarmDataManager(data_dir="swarm_data")
    swarm_a, swarm_b, swarm_c = manager.download_for_trajectory(gps_df)
    ```

## What's New in v0.2.0

The latest version introduces significant improvements:

!!! info "Major Enhancements"
    - **SwarmDataManager Class**: Improved data management with persistent storage
    - **Enhanced Parallel Processing**: Dramatically improved performance for large datasets
    - **CLI Interface**: Command-line tools for batch processing and automation
    - **Better Error Handling**: Robust error management and detailed logging
    - **Multiple Data Formats**: Flexible storage options (Parquet, CSV)
    - **Resume Capability**: Continue interrupted downloads automatically

## Getting Started?

-  **Need to start**
    ---
    New to MagGeo? Start here for installation, setup, and your first analysis.
    [Installation Guide](getting-started/installation.md)

-  **User Guide**
    ---
    Comprehensive guides for all MagGeo features and workflows.
    [User Guide](user-guide/basic-usage.md)
-  **API Reference**
    ---
    Detailed documentation of all classes, functions, and methods.
    [:octicons-arrow-right-24: API Reference](api/index.md)
- **Examples**
    ---
    Real-world examples, tutorials, and Jupyter notebooks.
    [Examples](examples/basic.md)

##  Community & Support
We welcome contributions and feedback!

- **Report Issues**: [GitHub Issues](https://github.com/fbenitez92/maggeo/issues)
- **Contribute**: [Contributing Guide](development/contributing.md)
- **Cite**: [Citation Information](about/citation.md)

---