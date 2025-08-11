import numpy as np
import pandas as pd

def distance_to_GPS(s_lat, s_lng, e_lat, e_lng):
    """ Calculate the distance between two GPS coordinates.

    This function uses the Haversine formula to compute the distance between two points on the Earth specified by their latitude and longitude.
    It returns the distance in kilometers.
    
    Parameters
    ----------
    s_lat : float
        Starting latitude in degrees.
    s_lng : float
        Starting longitude in degrees.
    e_lat : float
        Ending latitude in degrees.
    e_lng : float
        Ending longitude in degrees.
    Returns
    -------
    float
        Distance in kilometers between the two GPS coordinates.
    """
    # Haversine formula to calculate the distance between two points on the Earth
    # Reference: https://en.wikipedia.org/wiki/Haversine_formula
    
    R = 6373.0
    # approximate radius of earth in km
    s_lat = s_lat*(np.pi)/180.0                     
    s_lng = np.deg2rad(s_lng)     
    e_lat = np.deg2rad(e_lat)                       
    e_lng = np.deg2rad(e_lng)
    d = np.sin((e_lat - s_lat)/2)**2 + np.cos(s_lat)*np.cos(e_lat) * np.sin((e_lng - s_lng)/2)**2
    return 2 * R * np.arcsin(np.sqrt(d))

def Kradius(lat):
    """
    Calculate the radius of the Earth at a given latitude.

    Parameters
    ----------
    lat : float
        Latitude in degrees. Must be in the range (-90, 90), exclusive.

    Returns
    -------
    float
        Radius in kilometers at the given latitude.

    Raises
    ------
    ValueError
        If latitude is not in the range (-90, 90).
    """
    if 0 <= lat < 90:
        # for Northern Latitudes 
        nlat = (-10 * lat) + 1800
        #print("The R on the North")
    elif -90 < lat < 0:
        # for Southern Latitudes
        nlat = (10 * lat) + 1800
        #print ("The R on the South")
    else:
        raise ValueError("Latitude must be between -90 and 90 degrees (exclusive).")
    return nlat


def DistJ(ds, r, dt, DT):
    """
    Calculate the distance between two points in a geodetic frame
    See the paper "Fusion of wildlife tracking and satellite geomagnetic data for the study of animal migration" by Benitez-Paez et al. (2023) for more details.
    Parameters
    ----------
    ds : float
        Distance in the North-South direction.
    r : float
        Radius of the Earth at the given latitude.
    dt : float
        Distance in the East-West direction.
    DT : float
        Time difference in seconds.
    
    Returns
    -------
    float
        Distance in kilometers between the two points.
    """
    eDist = np.sqrt(((ds/r)**2 + (dt/DT)**2)/2)
    return eDist

def DfTime_func(SwarmData, GPSTime, DT):
    """
    Extract a DataFrame for a specific GPS time and its surrounding data.

    Parameters
    ----------
    SwarmData : pd.DataFrame
        DataFrame containing Swarm data indexed by time.
    GPSTime : pd.Timestamp
        The GPS time for which to extract the DataFrame in Epoch format.
    DT : pd.Timedelta
        Time delta to define the range around GPSTime.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the data for the specified GPS time and its surrounding data.
        If `GPSTime` is not found in the index, returns an empty DataFrame.
    """
    # Check if GPSTime is in the index of SwarmData
    import logging
    logging.debug("Entered DfTime_func")
    if GPSTime in SwarmData.index:
        logging.debug(f"Extracting data for GPSTime: {GPSTime} with DT: {DT}")
        # Extract the DataFrame for the specified GPS time and its surrounding data
        logging.debug(f"Yes the GPSTime is in the index of SwarmData:{GPSTime}, should be the same")
        return SwarmData.loc[GPSTime-DT:GPSTime+DT]
    else:
        logging.debug(f"GPSTime {GPSTime} not found in SwarmData index. Returning empty DataFrame.")
        return pd.DataFrame()
    
def gg_to_geo(h, gdcolat):
    """
Compute geocentric colatitude and radius from geodetic colatitude and height.

Parameters
----------
h : ndarray, shape (...) Altitude in kilometers.

gdcolat : ndarray, shape (...) Geodetic colatitude

Returns
-------
radius : ndarray, shape (...) Geocentric radius in kilometers.

theta : ndarray, shape (...) Geocentric colatitude in degrees.

sd : ndarray shape (...)  rotate B_X to gd_lat 

cd : ndarray shape (...) rotate B_Z to gd_lat 

References
----------

* Equations (51)-(53) from "The main field" (chapter 4) by Langel, R. A. in:

"Geomagnetism", Volume 1, Jacobs, J. A., Academic Press, 1987.

* Malin, S.R.C. and Barraclough, D.R., 1981. An algorithm for synthesizing 

the geomagnetic field. Computers & Geosciences, 7(4), pp.401-405.

"""

# Use WGS-84 ellipsoid parameters

    eqrad = 6378.137 # equatorial radius

    flat = 1/298.257223563 

    plrad = eqrad*(1-flat) # polar radius

    ctgd = np.cos(np.deg2rad(gdcolat))

    stgd = np.sin(np.deg2rad(gdcolat))

    a2 = eqrad*eqrad

    a4 = a2*a2

    b2 = plrad*plrad

    b4 = b2*b2

    c2 = ctgd*ctgd

    s2 = 1-c2

    rho = np.sqrt(a2*s2 + b2*c2)

    rad = np.sqrt(h*(h+2*rho) + (a4*s2+b4*c2)/rho**2)

    cd = (h+rho)/rad

    sd = (a2-b2)*ctgd*stgd/(rho*rad)

    cthc = ctgd*cd - stgd*sd # Also: sthc = stgd*cd + ctgd*sd

    thc = np.rad2deg(np.arccos(cthc)) # arccos returns values in [0, pi]

    return rad, thc, sd, cd