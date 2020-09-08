import pandas as pd
import numpy as np
import os
import pandas as pd
import timeit, sys
from datetime import datetime
import time
from datetime import timedelta
import datetime as dt
import calendar

from DfTime_func import DfTime_func
from distance_to_GPS import distance_to_GPS
from Kradius import Kradius
from DistJ import DistJ

SwarmA = pd.read_csv('SwarmDataA.csv',low_memory=False, index_col='epoch')
SwarmA['Ta'] = pd.to_datetime(SwarmA['Ta'])
SwarmB = pd.read_csv('SwarmDataB.csv',low_memory=False, index_col='epoch')
SwarmB['Tb'] = pd.to_datetime(SwarmB['Tb'])
SwarmC = pd.read_csv('SwarmDataC.csv',low_memory=False, index_col='epoch')
SwarmC['Tc'] = pd.to_datetime(SwarmC['Tc'])


def SwarmMagAnnotation (GPSLat,GPSLong,GPSDateTime,GPSTime,DT):

    DfTimeA = DfTime_func(SwarmA,GPSTime,DT)
    DfTimeB = DfTime_func(SwarmB,GPSTime,DT)
    DfTimeC = DfTime_func(SwarmC,GPSTime,DT)

    DfTimeA['dTa'] = (GPSTime - (DfTimeA.index))
    DfTimeB['dTb'] = (GPSTime - (DfTimeB.index))
    DfTimeC['dTc'] = (GPSTime - (DfTimeC.index))
    
    ## Parsed the requiered parameters...
    s_lat = GPSLat; e_lat = DfTimeA['LatA']; s_lng = GPSLong; e_lng = DfTimeA['LongA']  

        ##2.3 Running the function, based on the previous parameters, for SatA
    DfTimeA['distance']= distance_to_GPS(s_lat, s_lng, e_lat, e_lng) 

    s_lat = GPSLat; e_lat = DfTimeB['LatB']; s_lng = GPSLong; e_lng = DfTimeB['LongB']  

        #2.4 Running the function, based on the previous parameters, for SatB
    DfTimeB['distance']= distance_to_GPS(s_lat, s_lng, e_lat, e_lng) 

    s_lat = GPSLat; e_lat = DfTimeC['LatC']; s_lng = GPSLong; e_lng = DfTimeC['LongC']  

        #2.5 Running the function, based on the previous parameters, for SatC
    DfTimeC['distance']= distance_to_GPS(s_lat, s_lng, e_lat, e_lng) 
        
    DfTimeA['r']= Kradius(GPSLat)
    DfTimeB['r']= Kradius(GPSLat)
    DfTimeC['r']= Kradius(GPSLat)

    dfFinalA=DfTimeA[DfTimeA['distance']<=DfTimeA['r']]
    dfFinalB=DfTimeB[DfTimeB['distance']<=DfTimeB['r']]
    dfFinalC=DfTimeC[DfTimeC['distance']<=DfTimeC['r']]

    NumSatA = len(dfFinalA.index)
    NumSatB = len(dfFinalB.index)
    NumSatC = len(dfFinalC.index)
    TolSatPts = (NumSatA+NumSatB+NumSatC)
    
    dfFinalA.drop(['Ta'], axis=1, inplace=True) 
    dfFinalB.drop(['Tb'], axis=1, inplace=True)
    dfFinalC.drop(['Tc'], axis=1, inplace=True)
        
    dfFinalA.rename(columns={"LatA": "Lat", "LongA": "Long", "Na": "N", "Ea": "E", "Ca": "C", "dTa": "dT"}, inplace=True)
    dfFinalB.rename(columns={"LatB": "Lat", "LongB": "Long", "Nb": "N", "Eb": "E", "Cb": "C", "dTb": "dT"}, inplace=True)
    dfFinalC.rename(columns={"LatC": "Lat", "LongC": "Long", "Nc": "N", "Ec": "E", "Cc": "C", "dTc": "dT"}, inplace=True)

    frames = [dfFinalA, dfFinalB, dfFinalC] #List to index the specific SatId to the new full DF.
    SwarmData = pd.concat(frames, keys=['A', 'B', 'C'], sort=False)
    
    MinDistance = SwarmData['distance'].min()
    AvDistance = SwarmData['distance'].mean()
    
    ds = SwarmData['distance']
    r = SwarmData['r']
    dt = SwarmData['dT']

    SwarmData['Dj']= DistJ(ds, r, dt, DT)
   
    SwarmData['W']= 1/((SwarmData['Dj'])**2)
    
    SumW = SwarmData['W'].sum()
    SwarmData['Wj'] = SwarmData['W']/SumW
    
    Ngps = (SwarmData['Wj']*SwarmData['N']).sum()
    Egps = (SwarmData['Wj']*SwarmData['E']).sum()
    Cgps = (SwarmData['Wj']*SwarmData['C']).sum()

    Hgps = np.sqrt((Ngps**2)+(Egps**2))
    DgpsRad = np.arctan(Egps/Ngps)
    Dgps = np.degrees(DgpsRad)
    Fgps = np.sqrt((Ngps**2)+(Egps**2)+(Cgps**2))
    IgpsRad = np.arctan(Cgps/Hgps)
    Igps = np.degrees(IgpsRad)
    resultrow = {'Latitude': GPSLat, 'Longitude': GPSLong, 'DateTime': GPSDateTime, 'Fgps':Fgps, 'N': Ngps, 'E': Egps, 'C':Cgps, 'H':Hgps, 'D':Dgps,'I':Igps, 'TotalPoints':TolSatPts, 'MinDist':MinDistance, 'AvDist':AvDistance}  
    return resultrow