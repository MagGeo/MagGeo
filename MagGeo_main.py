"""
Core MagGeo_Sequential Model
Created on Thur Feb 17, 22
Updated on Sun Jul 27, 25
@author: Fernando Benitez-Paez
"""

import datetime as dt
from datetime import timedelta
import sys,os
from matplotlib.pyplot import pause
import pandas as pd
import numpy as np
from tqdm import tqdm
import click

from yaml import load, SafeLoader
from viresclient import set_token

sys.path.append("utilities")
from utilities.MagGeoFunctions import getGPSData
from utilities.MagGeoFunctions import Get_Swarm_residuals
from utilities.MagGeoFunctions import ST_IDW_Process
from utilities.MagGeoFunctions import CHAOS_ground_values


@click.command()
@click.option('-p',
              '--parameters-file',
              type=click.Path(exists=True),
              help="Parameters file to use to configure the model.")
@click.option('--token',
              help="Enter your VirES Token.")


def main(parameters_file, token):
    """
    Main function which get the data from Swarm VirES client
    """

    print(f"--\nReading parameters file: {parameters_file}\n--")

    set_token(token=token)


    try:
        with open(parameters_file, 'r') as f:

            parameters = load(f,
                              Loader=SafeLoader)
            maggeo_params = parameters["maggeo"] 
            gpsfilename = maggeo_params["gpsfilename"]
            Lat = maggeo_params["Lat"]
            Long = maggeo_params["Long"] 
            DateTime = maggeo_params["DateTime"]
            altitude = maggeo_params["altitude"]

    except Exception as error:
        print('Error in parameters file format')
        raise error
    
    base_dir=os.getcwd()
    temp_results_dir = os.path.join(base_dir, "temp_data")
    results_dir = os.path.join(base_dir, "results")
    data_dir = os.path.join(base_dir, "data")
    utilities_dir = os.path.join(base_dir, "utilities")

    GPSData = getGPSData(data_dir,gpsfilename,Lat,Long,DateTime,altitude)
    
    datestimeslist = []
    for index, row in GPSData.iterrows():
        datetimerow  = row['gpsDateTime']
        daterow = row['dates']
        hourrow = row['times']
        hourrow = hourrow.strftime('%H:%M:%S')
        if hourrow < '04:00:00':
            date_bfr = daterow - (timedelta(days=1))
            datestimeslist.append(daterow)
            datestimeslist.append(date_bfr)
        if hourrow > '20:00:00':
            Date_aft = daterow + (timedelta(days=1))
            datestimeslist.append(daterow)
            datestimeslist.append(Date_aft)  
        else:
            datestimeslist.append(daterow)

    def uniquelistdates(list): 
        x = np.array(list) 
        uniquelist = np.unique(x)
        return uniquelist

    uniquelist_dates = uniquelistdates(datestimeslist)

    hours_t_day = 24 #MagGeo needs the entire Swarm data for each day of the identified day.
    hours_added = dt.timedelta(hours = hours_t_day)

    listdfa = []
    listdfb = []
    listdfc = []

    for d in tqdm(uniquelist_dates, desc="Getting Swarm Data"):
        #print("Getting Swarm data for date:",d )
        startdate = dt.datetime.combine(d, dt.datetime.min.time())
        enddate = startdate + hours_added
        SwarmResidualsA,SwarmResidualsB,SwarmResidualsC = Get_Swarm_residuals(startdate, enddate)
        listdfa.append(SwarmResidualsA)
        listdfb.append(SwarmResidualsB)
        listdfc.append(SwarmResidualsC)

    base_dir = os.getcwd()  # Get main MagGeo directory
    temp_results_dir = os.path.join(base_dir, "temp_data")
    results_dir = os.path.join(base_dir, "results")
    data_dir = os.path.join(base_dir, "data")

    #TODO:
    #Find a more elegant way to concat the the list from Swarm and then read it to get the type of columns is required, Timestamp as datetime and epoch as index.
    
    PdSwarmRes_A = pd.concat(listdfa, join='outer', axis=0)
    PdSwarmRes_A.to_csv (os.path.join(temp_results_dir,'TotalSwarmRes_A.csv'), header=True)
    PdSwarmRes_B = pd.concat(listdfb, join='outer', axis=0)
    PdSwarmRes_B.to_csv (os.path.join(temp_results_dir,'TotalSwarmRes_B.csv'), header=True)
    PdSwarmRes_C = pd.concat(listdfc, join='outer', axis=0)
    PdSwarmRes_C.to_csv (os.path.join(temp_results_dir,'TotalSwarmRes_C.csv'), header=True)

    TotalSwarmRes_A = pd.read_csv(os.path.join(temp_results_dir,"TotalSwarmRes_A.csv"),low_memory=False, index_col='epoch')
    TotalSwarmRes_A['timestamp'] = pd.to_datetime(TotalSwarmRes_A['timestamp'])
    TotalSwarmRes_B = pd.read_csv(os.path.join(temp_results_dir,"TotalSwarmRes_B.csv"),low_memory=False, index_col='epoch')
    TotalSwarmRes_B['timestamp'] = pd.to_datetime(TotalSwarmRes_B['timestamp'])
    TotalSwarmRes_C = pd.read_csv(os.path.join(temp_results_dir,"TotalSwarmRes_C.csv"),low_memory=False, index_col='epoch')
    TotalSwarmRes_C['timestamp'] = pd.to_datetime(TotalSwarmRes_C['timestamp'])

    dn = [] ## List used to add all the GPS points with the annotated MAG Data. See the last bullet point of this process        
    for index, row in tqdm(GPSData.iterrows(), total=GPSData.shape[0], desc="Annotating the GPS Trajectory"):
        GPSLat = row['gpsLat']  
        GPSLong = row['gpsLong']
        GPSDateTime = row['gpsDateTime']
        GPSTime = row['epoch']
        GPSAltitude = row['gpsAltitude']
        #print("Process for:", index,"DateTime:",GPSDateTime)
        try:
            result=ST_IDW_Process(GPSLat,GPSLong,GPSAltitude, GPSDateTime,GPSTime, TotalSwarmRes_A, TotalSwarmRes_B, TotalSwarmRes_C)
            dn.append(result)
        except:
            #print("Ups!.That was a bad Swarm Point, let's keep working with the next point")
            result_badPoint= {'Latitude': GPSLat, 'Longitude': GPSLong, 'Altitude':GPSAltitude, 'DateTime': GPSDateTime, 'N_res': np.nan, 'E_res': np.nan, 'C_res':np.nan, 'TotalPoints':0, 'Minimum_Distance':np.nan, 'Average_Distance':np.nan}  
            dn.append(result_badPoint)
            continue
    
    
    GPS_ResInt = pd.DataFrame(dn)
    GPS_ResInt.to_csv (os.path.join(temp_results_dir,"GPS_ResInt.csv"), header=True)
    
    X_obs, Y_obs, Z_obs, X_obs_internal, Y_obs_internal, Z_obs_internal = CHAOS_ground_values(utilities_dir,GPS_ResInt)

    GPS_ResInt['N'] =pd.Series(X_obs)
    GPS_ResInt['E'] =pd.Series(Y_obs)
    GPS_ResInt['C'] =pd.Series(Z_obs)
    GPS_ResInt['N_Obs'] =pd.Series(X_obs_internal)
    GPS_ResInt['E_Obs'] =pd.Series(Y_obs_internal)
    GPS_ResInt['C_Obs'] =pd.Series(Z_obs_internal)

    GPS_ResInt.drop(columns=['N_res', 'E_res','C_res'], inplace=True)

    # Having Interpolated and weighted the magnetic values, we can compute the other magnetic components. 
    GPS_ResInt['H'] = np.sqrt((GPS_ResInt['N']**2)+(GPS_ResInt['E']**2))
    #check the arcgtan in python., From arctan2 is saver.
    DgpsRad = np.arctan2(GPS_ResInt['E'],GPS_ResInt['N'])
    GPS_ResInt['D'] = np.degrees(DgpsRad)
    IgpsRad = np.arctan2(GPS_ResInt['C'],GPS_ResInt['H'])
    GPS_ResInt['I'] = np.degrees(IgpsRad)
    GPS_ResInt['F'] = np.sqrt((GPS_ResInt['N']**2)+(GPS_ResInt['E']**2)+(GPS_ResInt['C']**2))

    
    originalGPSTrack=pd.read_csv(os.path.join(data_dir,gpsfilename))
    MagGeoResult = pd.concat([originalGPSTrack, GPS_ResInt], axis=1)
    #Drop duplicated columns. Latitude, Longitude, and DateTime will not be part of the final result.
    MagGeoResult.drop(columns=['Latitude', 'Longitude', 'DateTime'], inplace=True)
    
    #Exporting the CSV file
    
    outputfile ="GeoMagResult_"+gpsfilename
    export_csv = MagGeoResult.to_csv (os.path.join(results_dir,outputfile), index = None, header=True)    
    print("Congrats! MagGeo has processed your GPS trajectory. Find the annotated table: " + outputfile + " in the folder results.")

if __name__ == '__main__':
    main()
    print("End of MagGeo")