import numpy as np

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

def gg_to_geo(h, gdcolat):

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