# MagGeo: GPS Trajectory Annotation with Geomagnetic Data

[![PyPI version](https://badge.fury.io/py/maggeo.svg)](https://badge.fury.io/py/maggeo)
[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.4543735.svg)](https://zenodo.org/badge/latestdoi/289120794)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**MagGeo** is a Python package to annotate GPS trajectories with geomagnetic data from ESA's Swarm satellite constellation. This tool enables researchers to annotate animal movement data with Earth's magnetic field measurements for animal movement analytics research.

## Key Features

- **GPS Trajectory Annotation**: Enrich GPS tracks with geomagnetic field components (N, E, C, H, D, I, F) and optionally witih indices (Kp, AE, SME)
- **High Performance**: 5.6x faster processing compared to the previous version.
- **Parallel Processing**: Efficient handling of large datasets so it can process large GPS trajectories in parallel.
- **Swarm Data Integration**: Direct access to ESA Swarm satellite geomagnetic data through the ViRES platform.
- **Geomagnetic Indices**: Integration with AE and SME geomagnetic activity indices for enhanced analysis.
- **Command Line Interface**: User-friendly CLI for batch processing and automation
- **Comprehensive Documentation**: Complete Research and API documentation with examples and tutorials.

## Documentation

- **Full Documentation**: [MagGeo.github.io/MagGeo](https://MagGeo.github.io/MagGeo) *(available after publication)*
- **Quick Start Guide**: [Getting Started](https://MagGeo.github.io/MagGeo/getting-started/quickstart/)
- **API Reference**: [API Documentation](https://MagGeo.github.io/MagGeo/api/)
- **Examples**: [Usage Examples](https://MagGeo.github.io/MagGeo/examples/)

## Installation

### Quick Install (Recommended)

```bash
pip install maggeo
```

### Development Install

```bash
# Clone the repository
git clone https://github.com/MagGeo/MagGeo.git
cd MagGeo

# Install in development mode
pip install -e ".[dev,docs]"
```

### Dependencies

MagGeo requires Python 3.8+ and depends on:
- `numpy`, `scipy`, `pandas` - Core data processing
- `matplotlib` - Visualization capabilities  
- `viresclient` - Swarm satellite data access
- `chaosmagpy` - CHAOS geomagnetic model
- `click` - Command-line interface
- `tqdm` - Progress bars for long operations

## Quick Start

### Python API

```python
import pandas as pd
from maggeo.core import annotate_gps_with_geomag

# Load your GPS trajectory data
gps_data = pd.read_csv('your_trajectory.csv')

# Annotate with geomagnetic data
annotated_data = annotate_gps_with_geomag(
    gps_data,
    lat_col='latitude',
    lon_col='longitude', 
    datetime_col='datetime',
    altitude_col='altitude',  # Optional altitude column
    token='your_vires_token',  # ViRES API token for Swarm data access
)

# Save results
annotated_data.to_csv('trajectory_with_geomag.csv', index=False)
```

### Command Line Interface

```bash
# Annotate a GPS trajectory file
maggeo annotate trajectory.csv --output annotated_trajectory.csv

# Download Swarm satellite data
maggeo swarm --start-date 2023-01-01 --end-date 2023-01-31

# Validate GPS file format
maggeo validate trajectory.csv

# Get package information
maggeo info
```

### Advanced Usage with Parallel Processing

```python
from maggeo.parallel_processing import parallel_maggeo_annotation
from maggeo.swarm_data_manager import SwarmDataManager

# For large datasets, use parallel processing
large_dataset = pd.read_csv('large_trajectory.csv')

annotated_data = parallel_maggeo_annotation(
    large_dataset,
    chunk_size=1000,  # Optimize based on your system
    n_jobs=-1         # Use all available cores
)

# Manage Swarm data efficiently
manager = SwarmDataManager()
swarm_data = manager.download_swarm_data(
    start_date='2023-01-01',
    end_date='2023-01-31',
    satellite='A'
)
```

## What's New in v0.2.0

This major refactor of MagGeo and introduces significant improvements:

### Performance Enhancements
- **5.6x faster** processing for large trajectories
- **Optimized memory usage** with efficient data structures
- **Smart chunking** for parallel processing 

### New Features
- **SwarmDataManager**: Unified interface for Swarm data handling
- **Enhanced CLI**: Four comprehensive commands for all workflows
- **Geomagnetic Indices**: AE and SME index integration
- **Improved Error Handling**: Better validation and user feedback

### Developer Experience
- **Modern Package Structure**: PyPI-ready with `pyproject.toml`
- **Comprehensive Documentation**: MkDocs Material with API reference and Research documentation.
- **Enhanced Testing**: Expanded test suite with better coverage

## Project Lineage

### Version 1.0 (2023)  
- **Initial Release**: Initial functionality for trajectory annotation and repository setup, it uses Jupyter notebooks for examples and documentation.

### Version 2.0 (2025) - **Current**
- **Major Refactor**: Complete codebase restructuring for performance and usability
- **Production Ready**: Professional packaging, documentation, and testing
- **Enhanced Capabilities**: 5.6x performance improvement and expanded feature set
- **Open Science**: Full PyPI publication for broader scientific community access

## Citation

If you use MagGeo in your research, please cite both the original methodology paper and the software:

### Primary Citation (Required)
```
Benitez-Paez, F., Brum-Bastos, V.d., Beggan, C.D. et al. Fusion of wildlife tracking and 
satellite geomagnetic data for the study of animal migration. Mov Ecol 9, 31 (2021). 
https://doi.org/10.1186/s40462-021-00268-4
```

### Software Citation (Recommended)
```
Benitez-Paez, F., Demšar, U., Long, J. A., & Beggan, C. D. (2025). MagGeo: A Python package 
for fusion of GPS trajectories and satellite geomagnetic data (Version 0.2.0) [Computer software]. 
https://github.com/MagGeo/MagGeo
```

📋 **[Complete citation guidelines with multiple formats →](https://MagGeo.github.io/MagGeo/about/citation/)**

## Authors & Initial Contributors

- **Fernando Benitez-Paez** - *Lead Author and Developer* - University of St Andrews
- **Urška Demšar** - *Principal Investigator* - University of St Andrews  
- **Jed A. Long** - *Co-Investigator* - University of Western Ontario
- **Vanessa Brum-Bastos** - *Co-Investigator* - University of Canterbury
- **Ciarán D. Beggan** - *Geomagnetic Expert* - British Geological Survey

**Contact:** [Fernando.Benitez@st-andrews.ac.uk](mailto:Fernando.Benitez@st-andrews.ac.uk)

## Contributing

We welcome contributions from the scientific community! Please see our [Contributing Guidelines](https://MagGeo.github.io/MagGeo/about/CONTRIBUTING/) for details on:

- 🐛 **Bug Reports**: Help us improve by reporting issues
- 💡 **Feature Requests**: Suggest new capabilities for movement ecology research  
- 🔧 **Code Contributions**: Submit pull requests for enhancements
- 📖 **Documentation**: Improve guides and examples
- 🧪 **Scientific Validation**: Share use cases and research applications

## License

MagGeo is released under the [MIT License](LICENSE), allowing free use for academic and commercial applications with proper attribution.

## Acknowledgments

- **ESA Swarm Mission** - For providing high-quality geomagnetic satellite data
- **VirES Platform** - For accessible Swarm data distribution
- **Max Planck Institute of Animal Behavior** - For feedback and Ecological validation
- **Leverhulme Trust Grant** - For funding support of the original research

---

## Links

| Resource | Link |
|----------|------|
| 📦 PyPI Package | https://pypi.org/project/maggeo/ |
| 📖 Documentation | https://MagGeo.github.io/MagGeo |
| 🐙 GitHub Repository | https://github.com/MagGeo/MagGeo |
| 📄 Original Paper | https://doi.org/10.1186/s40462-021-00268-4 |
| 🎯 Issue Tracker | https://github.com/MagGeo/MagGeo/issues |

---

# Contact us

**MagGeo** is work in progress and we are constantly making improvements that you can follow up with the commits made in the pubic GitHub repo. For general enquiries, scientific concepts, suggestions please email: [Fernando.Benitez@st-andrews.ac.uk](mailto:fbenitez@turing.ac.uk), [ud2@st-andrews.ac.uk](mailto:ud2@st-andrews.ac.uk), [jed.long@uwo.ca](mailto:jed.long@uwo.ca)

For **errors**, or **improvements** please submit an issue in this repo, describing the problem you have.

