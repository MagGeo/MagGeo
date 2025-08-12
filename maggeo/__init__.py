# maggeo/__init__.py
"""
MagGeo: Data fusion library for annotating GPS trajectories with geomagnetic satellite data from Swarm mission from ESA.
Authors: Fernando Benitez-Paez, Urška Demšar, Jed Long, Ciaran Beggan

This package materialise a data fusion method to annotate GPS trajectories with geomagnetic data from the Swarm satellite mission.
It includes functions for data retrieval, processing, and annotation, as well as debugging utilities.
For more information, please refer to the paper:

Benitez-Paez, F., Brum-Bastos, V.d., Beggan, C.D. et al. 
Fusion of wildlife tracking and satellite geomagnetic data for the study of animal migration. 
Mov Ecol 9, 31 (2021). https://doi.org/10.1186/s40462-021-00268-4

"""

__version__ = "0.2.1"
__author__ = "Fernando Benitez-Paez, Urška Demšar, Jed Long, Ciaran Beggan"
__email__ = "Fernando.Benitez@st-andrews.ac.uk"

# Lazy imports to avoid immediate dependency loading
def get_main_function():
    """Get the main annotation function with lazy import."""
    try:
        from .core import annotate_gps_with_geomag
        return annotate_gps_with_geomag
    except ImportError as e:
        raise ImportError(f"Could not import core functionality. Please ensure all dependencies are installed: {e}")

# Only expose main function, date utilities, indices, parallel functions, and swarm data manager to avoid import issues
__all__ = ['annotate_gps_with_geomag', 'identify_unique_dates', 'get_ae_index', 'get_sme_index', 'merge_indices_with_maggeo', 
           'SwarmDataManager', 'download_swarm_data_for_trajectory', 'load_swarm_data', 
           'parallel_row_handler', 'parallel_st_idw_process', 'parallel_chaos_ground_values', '__version__']

# Make main function, date utilities, indices, parallel functions, and swarm data manager available
try:
    from .core import annotate_gps_with_geomag
    from .date_utils import identify_unique_dates
    from .parallel_processing import parallel_row_handler
    from .interpolation import parallel_st_idw_process
    from .chaos import parallel_chaos_ground_values
    from .indices import get_ae_index, get_sme_index, merge_indices_with_maggeo
    from .swarm_data_manager import SwarmDataManager, download_swarm_data_for_trajectory, load_swarm_data
except ImportError:
    # Provide informative error message
    def annotate_gps_with_geomag(*args, **kwargs):
        raise ImportError(
            "MagGeo core functionality is not available. "
            "Please ensure all dependencies are installed:\n"
            "pip install viresclient chaosmagpy pandas netCDF jupyterlab \n"
            "or install MagGeo with conda using the provided environment.yml"
        )
    
    def identify_unique_dates(*args, **kwargs):
        raise ImportError(
            "MagGeo core functionality is not available. "
            "Please ensure all dependencies are installed:\n"
            "pip install viresclient chaosmagpy pandas netCDF jupyterlab hapiclient \n"
            "or install MagGeo with conda using the provided environment.yml"
        )
    
    def get_ae_index(*args, **kwargs):
        raise ImportError(
            "MagGeo indices functionality is not available. "
            "Please ensure all dependencies are installed:\n"
            "pip install hapiclient pandas numpy \n"
            "or install MagGeo with conda using the provided environment.yml"
        )
    
    def get_sme_index(*args, **kwargs):
        raise ImportError(
            "MagGeo indices functionality is not available. "
            "Please ensure all dependencies are installed:\n"
            "pip install hapiclient pandas numpy \n"
            "or install MagGeo with conda using the provided environment.yml"
        )
    
    def merge_indices_with_maggeo(*args, **kwargs):
        raise ImportError(
            "MagGeo indices functionality is not available. "
            "Please ensure all dependencies are installed:\n"
            "pip install hapiclient pandas numpy \n"
            "or install MagGeo with conda using the provided environment.yml"
        )