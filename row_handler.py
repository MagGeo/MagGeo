import pandas as pd
import numpy as np
import os
from SwarmMagAnnotation import SwarmMagAnnotation

def row_handler (GPSData,DT):
    dn = [] ## List used to add all the GPS points with the annotated MAG Data. See the last bullet point of this process        
    for index, row in GPSData.iterrows():
        GPSLat = row['gpsLat']
        GPSLong = row['gpsLong']
        GPSDateTime = row['gpsDateTime']
        GPSTime = row['epoch']
        print("Process for:", index,"Epoch:",GPSDateTime)
        result=SwarmMagAnnotation(GPSLat,GPSLong,GPSDateTime,GPSTime,DT)
        dn.append(result)
    return pd.DataFrame(dn)