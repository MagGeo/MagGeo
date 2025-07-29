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

#### 1. Read the parameters file available in the parameters folder.
#    The parameters file is a YAML file that contains the parameters to run the MagGeo model
#    The parameters file should contain the following keys:
#    - gpsfilename: The name of the GPS file to be processed.
#    - Lat: The latitude of the GPS trajectory.
#    - Long: The longitude of the GPS trajectory.
#    - DateTime: The timestamp of the GPS trajectory.
#    - altitude: The altitude of the GPS trajectory.        
#    - parallel-mode: Whether to run MagGeo in parallel mode for big GPS trajectories, TRUE for parallel mode.
@click.command()
@click.option('-p',
              '--parameters-file',
              type=click.Path(exists=True),
              help="Parameters file to use to configure the model.")
# --token option to enter the VirES token for accessing Swarm data, created in the ViRES client.
# This token is required to access the Swarm data from the VirES client.
# The token can be obtained from the ViRES client website.
# https://vires.services/vires-client/
# The token is stored in the ~/.vires/vires_token file.
# If the token is not provided, the user will be prompted to enter it.
# The token is used to authenticate the user and access the Swarm data.
# If the token is not provided, the user will be prompted to enter it.
@click.option('--token',
              help="Enter your VirES Token.")


def main(parameters_file, token):
    """
    1. Main function which get the data from Swarm VirES client
    2. Reads the parameters file and gets the GPS data.
    3. Gets the Swarm data for each day of the GPS trajectory.
    4. Annotates the GPS trajectory with the Swarm data.
    5. Computes the magnetic components from the Swarm data.
    6. Exports the annotated GPS trajectory with the magnetic components to a CSV file.
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
    
    # Here I check if the folder structure is correct, if not, I create the folders.
    # The folder structure is:
    # MagGeo/
    # ├── data/
    # ├── results/
    # ├── temp_data/
    # ├── utilities/
    # └── MagGeo_main.py
    # The data folder contains the GPS data file.
    # The results folder contains the annotated GPS trajectory with the magnetic components.
    # The temp_data folder contains the intermediate results of the Swarm data.
    base_dir=os.getcwd()
    temp_results_dir = os.path.join(base_dir, "temp_data")
    results_dir = os.path.join(base_dir, "results")
    data_dir = os.path.join(base_dir, "data")
    utilities_dir = os.path.join(base_dir, "utilities")

    # Here I Get the GPS data from the GPS file. I use the getGPSData function to read the GPS data.
    # The getGPSData function reads the GPS data from the GPS file and returns a pandas DataFrame with the GPS data.
    # The GPS data contains the following columns:
    # - gpsLat: The latitude of the GPS trajectory.
    # - gpsLong: The longitude of the GPS trajectory.
    # - gpsDateTime: The timestamp of the GPS trajectory.
    # - gpsAltitude: The altitude of the GPS trajectory.
    # - epoch: The epoch time of the GPS trajectory.
    # - dates: The date of the GPS trajectory.
    # - times: The time of the GPS trajectory.
    # The GPS data is used to get the Swarm data for each day of the GPS trajectory.
    # The GPS data is also used to annotate the GPS trajectory with the Swarm data.
    # The GPS data is also used to compute the magnetic components from the Swarm data.
    # The GPS data is also used to export the annotated GPS trajectory with the magnetic components to
    # a CSV file.   
    GPSData = getGPSData(data_dir,gpsfilename,Lat,Long,DateTime,altitude)
    
    # This is KEY.
    # Loops through GPS data. 
    # For each timestamp:
    #   If it's early morning (<04:00), add both current and previous date.
    #   If it's late evening (>20:00), add both current and next date.
    #   Otherwise, just add current date.
    #   Removes duplicates to get unique relevant dates.
    #   Prepares a 24-hour time delta for later use (e.g., fetching satellite data).
    # Assume GPSData has columns: 'gpsDateTime', 'dates' (datetime.date), 'times' (datetime.time)

    GPSData['time_str'] = GPSData['times'].apply(lambda t: t.strftime('%H:%M:%S'))

    # Flag early (< 04:00) and late (> 20:00) times
    early_mask = GPSData['time_str'] < '04:00:00'
    late_mask = GPSData['time_str'] > '20:00:00'

    # Start with current date
    datestimeslist = list(GPSData['dates'])

    # Add previous day for early times
    datestimeslist += list(GPSData.loc[early_mask, 'dates'] - timedelta(days=1))

    # Add next day for late times
    datestimeslist += list(GPSData.loc[late_mask, 'dates'] + timedelta(days=1))

    # Get unique, sorted dates
    uniquelist_dates = np.unique(datestimeslist)

    # 24-hour delta (if needed for fetching satellite data later), not really sure if this is used later
    # but it is used in the Get_Swarm_residuals function to fetch the Swarm data for each day.
    # This is used to ensure that we fetch the entire Swarm data for each day of the identified day.

    hours_t_day = 24 
    #MagGeo needs the entire Swarm data for each day of the identified day.
    hours_added = dt.timedelta(hours = hours_t_day)
    #Safety Sanity Debug Check
    print("Total relevant dates:", len(datestimeslist))
    print("Unique dates:", uniquelist_dates)    

    listdfa = []
    listdfb = []
    listdfc = []

    # Loop through each unique date and fetch Swarm data
    # The Get_Swarm_residuals function fetches the Swarm data for each date
    # The Get_Swarm_residuals function returns three pandas DataFrames:
    # - SwarmResidualsA: Swarm data for satellite A
    # - SwarmResidualsB: Swarm data for satellite B
    # - SwarmResidualsC: Swarm data for satellite C
    # The Swarm data is used to annotate the GPS trajectory with the Swarm data.
    # The Swarm data is also used to compute the magnetic components from the Swarm data
    # The Swarm data is also used to export the annotated GPS trajectory with the magnetic components
    # to a CSV file.
    print("Getting Swarm data for each date in the GPS trajectory...")
    
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
    # Find a more elegant way to concat the the list from Swarm and then read it to get the type of columns is required, Timestamp as datetime and epoch as index.
    # I did this because I need to have the Swarm data in a single DataFrame for each satellite.
    # This is done to have a single DataFrame for each satellite with the Swarm data
    # The Swarm data is used to annotate the GPS trajectory with the Swarm data.
    # The Swarm data is also used to compute the magnetic components from the Swarm data
    # The Swarm data is also used to export the annotated GPS trajectory with the magnetic components
    # to a CSV file.
    # The Swarm data is stored in the temp_data folder.
    # The Swarm data is stored in three separate DataFrames for each satellite.
    
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
            # If the ST_IDW_Process function fails, it means that there is no Swarm data for that GPS point.
            # In this case, we create a result with NaN values for the magnetic components and append it to the dn list.
            # This is done to ensure that we have a result for each GPS point, even if there is no Swarm data for that point.
            # This is done to ensure that we have a result for each GPS point, even if there is no Swarm data for that point.
            # The result will have NaN values for the magnetic components and the distance values.
            result_badPoint= {'Latitude': GPSLat, 'Longitude': GPSLong, 'Altitude':GPSAltitude, 'DateTime': GPSDateTime, 'N_res': np.nan, 'E_res': np.nan, 'C_res':np.nan, 'TotalPoints':0, 'Minimum_Distance':np.nan, 'Average_Distance':np.nan}  
            dn.append(result_badPoint)
            continue
    
    
    GPS_ResInt = pd.DataFrame(dn)
    GPS_ResInt.to_csv (os.path.join(temp_results_dir,"GPS_ResInt.csv"), header=True)
    
    # Now we have the GPS trajectory annotated with the Swarm data.
    # The GPS trajectory is stored in the GPS_ResInt DataFrame.
    # The GPS trajectory contains the following columns:
    # - Latitude: The latitude of the GPS trajectory.
    # - Longitude: The longitude of the GPS trajectory.
    # - Altitude: The altitude of the GPS trajectory.
    # - DateTime: The timestamp of the GPS trajectory.
    # - N_res: The North component of the magnetic field residuals.
    # - E_res: The East component of the magnetic field residuals.
    # - C_res: The Center component of the magnetic field residuals.
    # - TotalPoints: The total number of Swarm points that were filtered for that GPS point.
    # - Minimum_Distance: The minimum distance between the GPS point and the Swarm points that were filtered for that GPS point.
    # - Average_Distance: The average distance between the GPS point and the Swarm points that were filtered for that GPS point.
 
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

    # Now we have the GPS trajectory annotated with the Swarm data and the magnetic components.
    # the original GPS trajectory is read again to add the magnetic components.
    # the duplicated columns are dropped, and the final result is exported to a CSV file.
    # The final result contains the following columns:
    # - Latitude: The latitude of the GPS trajectory.
    # - Longitude: The longitude of the GPS trajectory.
    # - DateTime: The timestamp of the GPS trajectory.
    # - N: The North component of the magnetic field residuals.
    # - E: The East component of the magnetic field residuals.
    # - C: The Center component of the magnetic field residuals.
    # - N_Obs: The North component of the magnetic field observed.
    # - E_Obs: The East component of the magnetic field observed.
    # - C_Obs: The Center component of the magnetic field observed.
    # - H: The Horizontal component of the magnetic field.
    # - D: The Declination of the magnetic field.
    # - I: The Inclination of the magnetic field.
    # - F: The Total intensity of the magnetic field.
    # - TotalPoints: The total number of Swarm points that were filtered for that GPS point.
    # - Minimum_Distance: The minimum distance between the GPS point and the Swarm points
    #   that were filtered for that GPS point.
    # - Average_Distance: The average distance between the GPS point and the Swarm points
    #   that were filtered for that GPS point.
    # -kp_Avg: The average Kp index for the Swarm points that were filtered for that GPS point.

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