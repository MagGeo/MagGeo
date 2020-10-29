import numpy as np
import pandas as pd

def distance_to_GPS(s_lat, s_lng, e_lat, e_lng): 
    # approximate radius of earth in km
    R = 6373.0
    s_lat = s_lat*(np.pi)/180.0                     
    s_lng = np.deg2rad(s_lng)     
    e_lat = np.deg2rad(e_lat)                       
    e_lng = np.deg2rad(e_lng)
    d = np.sin((e_lat - s_lat)/2)**2 + np.cos(s_lat)*np.cos(e_lat) * np.sin((e_lng - s_lng)/2)**2
    return 2 * R * np.arcsin(np.sqrt(d))

def Kradius (lat):
    if 0 <= lat < 90 :
        #for Northern Latitudes 
        nlat = (-10 * lat) + 1800
        #print("The R on the North")
    if -90 < lat < 0:
        #for Southern Latitudes
        nlat = (10 * lat) + 1800
        #print ("The R on the South")
    return nlat

def DistJ(ds, r, dt, DT):
    eDist = np.sqrt(((ds/r)**2 + (dt/DT)**2)/2)
    return eDist

def DfTime_func (SwarmData, GPSTime, DT):
    DataFrame_Per_Time = []
    for index in SwarmData.index:
        if index == GPSTime:
            DataFrame_Per_Time = pd.DataFrame(SwarmData.loc[index-DT:index+DT])    
    return DataFrame_Per_Time