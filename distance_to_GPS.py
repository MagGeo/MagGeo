import numpy as np
def distance_to_GPS(s_lat, s_lng, e_lat, e_lng):
    # approximate radius of earth in km
    R = 6373.0
    s_lat = s_lat*(np.pi)/180.0                     
    s_lng = np.deg2rad(s_lng)     
    e_lat = np.deg2rad(e_lat)                       
    e_lng = np.deg2rad(e_lng)
    d = np.sin((e_lat - s_lat)/2)**2 + np.cos(s_lat)*np.cos(e_lat) * np.sin((e_lng - s_lng)/2)**2
    return 2 * R * np.arcsin(np.sqrt(d))
