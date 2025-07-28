"""
Custom exceptions for MagGeo library
@author: Fernando Benitez-Paez
date: July, 2025
"""


class MagGeoError(Exception):
    """Base exception for all MagGeo errors"""
    pass


class ValidationError(MagGeoError):
    """Raised when input data validation fails"""
    pass


class SwarmDataError(MagGeoError):
    """Raised when Swarm satellite data fetching fails"""
    pass


class InterpolationError(MagGeoError):
    """Raised when magnetic field interpolation fails"""
    pass


class CHAOSModelError(MagGeoError):
    """Raised when CHAOS model operations fail"""
    pass


class ConfigurationError(MagGeoError):
    """Raised when configuration is invalid"""
    pass