# MagGeo Documentation

Welcome to the **MagGeo API Documentation** - A comprehensive guide to GPS trajectory annotation with geomagnetic data from ESA's Swarm satellites.

## **For Developers & Package Users**


- **[Quick Start](getting-started/quickstart/)**
    ---
    Get MagGeo running in 5 minutes with installation and basic examples

- **[API Reference](api/)**
    ---
    Complete function reference with examples and parameters

- **[User Guide](user-guide/basic-usage.md)**
    ---
    Comprehensive guides for all MagGeo features and workflows

- **[Examples](examples/basic.md)**
    ---
    Practical examples from basic usage of MagGeo to advanced parallel processing


### **For Researchers**  

- **[Scientific Background](https://maggeo.github.io/MagGeo/science-behind/intro/)**
    ---
    Research methodology, and scientific foundation
- **[Key Concepts](https://maggeo.github.io/MagGeo/science-behind/background/)**
    ---
    Understanding geomagnetic data and its components

- **[How to Calculate Magnetic Components](https://maggeo.github.io/MagGeo/science-behind/calculation_mag_components/)**
    ---
    Explanation of how MagGeo calculate the geomagnetic components to the exact location and time of the GPS trajectory

- **[How does it work](https://maggeo.github.io/MagGeo/science-behind/how_does_it_works/)**
    ---
    How MagGeo processes GPS trajectories with geomagnetic data from satellite. 

<!-- - **[Case Studies](https://maggeo.github.io/case-studies/)**
    ---
    Use cases of MagGeo in wildlife tracking and migration studies
 -->
## **Package Information**

!!! info "Installation"
    ```bash
    pip install maggeo
    ```

!!! example "Quick Example"
    ```python
    import pandas as pd
    from maggeo.core import annotate_gps_with_geomag
    
    # Load GPS data
    gps_data = pd.read_csv('trajectory.csv')
    
    # Annotate with geomagnetic data
    result = annotate_gps_with_geomag(
        gps_data,
        lat_col='latitude',
        lon_col='longitude',
        datetime_col='datetime'
    )
    
    # Save annotated trajectory
    result.to_csv('annotated_trajectory.csv')
    ```

## **What's New in v0.2.0**

!!! success "Major Performance Improvements"
    - **5.6x faster** processing for large trajectories
    - **Enhanced parallel processing** with smart chunking
    - **SwarmDataManager** for unified data handling
    - **Comprehensive CLI** with 4 commands

## **Documentation Structure**

| Section | Purpose | Audience |
|---------|---------|----------|
| **[Getting Started](getting-started/)** | Installation, setup, first steps | All users |
| **[User Guide](user-guide/)** | Detailed usage instructions | Package users |
| **[API Reference](api/)** | Function documentation | Developers |
| **[Examples](examples/)** | Practical code examples | All users |
| **[Scientific Site →](https://maggeo.github.io/MagGeo/)** | Research background | Researchers |

## **Contributing**

We welcome contributions! See our [Contributing Guidelines](https://maggeo.github.io/contributing/) for:

- Bug reports and feature requests
- Documentation improvements  
- Code contributions
- Scientific validation and use cases

##  **Citation**

If you use MagGeo in your research, please cite:

!!! quote "Primary Citation"
    Benitez-Paez, F., Brum-Bastos, V.d., Beggan, C.D. et al. Fusion of wildlife tracking and satellite geomagnetic data for the study of animal migration. *Mov Ecol* **9**, 31 (2021). https://doi.org/10.1186/s40462-021-00268-4

[**Complete citation guide →**](./about/citation/)

---