from typing import Any, Dict
import pandas as pd
from .auxiliaryfunctions import distance_to_GPS, Kradius, DistJ, DfTime_func

def st_idw_process(
    gps_lat: float,
    gps_long: float,
    gps_altitude: float,
    gps_datetime: pd.Timestamp,
    gps_epoch: int,
    swarm_a: pd.DataFrame,
    swarm_b: pd.DataFrame,
    swarm_c: pd.DataFrame,
    dt_seconds: int = 14400
) -> Dict[str, Any]:
    """
    Interpolate Swarm residuals to a GPS point using spatiotemporal IDW.
    Returns a dictionary with interpolated values and metadata.
    """
    # This function performs the spatiotemporal inverse distance weighting (IDW) interpolation
    # for the Swarm residuals based on the GPS trajectory.
    # Interpolation of the Swarm Residuals., NEC interpolated residuals for each GPS Point. Quality flags filters.
    # Input:  GPS Trajectory columns, SwarmDataDF
    # Output: GPS Trajectory + ResidualsInterpolated

    # [REMOVE before Package Release]
    #print(f"=====")
    #print(f"[DEBUG] ST IDW Interpolation process with params: {gps_lat},{gps_long},{gps_altitude}, {gps_datetime}, {gps_epoch}, {dt_seconds}, {swarm_a.shape},{swarm_b.shape},{swarm_c.shape}")
    #print(f"=====")
    
    # 1. Running the DfTime_func function to filter by the defined DeltaTime.
    tk_a = DfTime_func(swarm_a, gps_epoch, dt_seconds)

    # [REMOVE before Package Release]
    #print(f"[DEBUG] tk_a len after DfTime_func: {len(tk_a)}")
    #print(f"=====")
    #print(f"=====")

    tk_b = DfTime_func(swarm_b, gps_epoch, dt_seconds)
    tk_c = DfTime_func(swarm_c, gps_epoch, dt_seconds)
    
    # [REMOVE before Package Release]
    #print(f"[DEBUG] tk_a shape after time filter: {tk_a.shape}")
    #print(tk_a.head())
    #tk_a.to_csv(f"temp_data/tk_a_{gps_epoch}.csv")
    #print(f"[DEBUG] tk_b shape after time filter: {tk_b.shape}")
    #print(tk_b.head())
    #tk_b.to_csv(f"temp_data/tk_b_{gps_epoch}.csv")
    #print(f"[DEBUG] tk_c shape after time filter: {tk_c.shape}")
    #print(tk_c.head())
    #tk_c.to_csv(f"temp_data/tk_c_{gps_epoch}.csv")

    #2. Computing the dt as the difference between the datetime and the datetime from swarm point. At this point
    # We have filtered the swarm point by time.

    # [REMOVE before Package Release]
    #print(f"=====")
    #print(f"[DEBUG] Computing time difference for tk_a, tk_b, tk_c with gps_epoch: {gps_epoch} and dt_seconds: {dt_seconds}")
    #print(f"=====")

    tk_a = tk_a.copy()
    tk_a['dT'] = (gps_epoch - tk_a.index)
    tk_b = tk_b.copy()
    tk_b['dT'] = (gps_epoch - tk_b.index) 
    tk_c = tk_c.copy()
    tk_c['dT'] = (gps_epoch - tk_c.index)

    # [REMOVE before Package Release]
    #print(f"[DEBUG] tk_a schema and shape: {tk_a.shape}")
    #print(tk_a.head(5))
    #tk_a.to_csv(f"temp_data/tk_a_{gps_epoch}_dT.csv")
    #tk_b.to_csv(f"temp_data/tk_b_{gps_epoch}_dT.csv")
    #tk_c.to_csv(f"temp_data/tk_c_{gps_epoch}_dT.csv")
    #print(f"=====")


    #3. Compute spatial distance (ds)
    ### Parsing the requires parameters for distance_to_GPS function

    # [REMOVE before Package Release]
    #print(f"=====")
    #print(f"[DEBUG] Computing spatial distance for tk_a, tk_b, tk_c with gps_lat: {gps_lat}, gps_long: {gps_long}, tk_a['Latitude'], tk_a['Longitude']")
    #print(f"=====")

    tk_a['distance'] = distance_to_GPS(gps_lat, gps_long, tk_a['Latitude'], tk_a['Longitude'])
    tk_b['distance'] = distance_to_GPS(gps_lat, gps_long, tk_b['Latitude'], tk_b['Longitude'])
    tk_c['distance'] = distance_to_GPS(gps_lat, gps_long, tk_c['Latitude'], tk_c['Longitude'])
    
    # [REMOVE before Package Release]
    #print(f"[DEBUG] tk_a schema and shape: {tk_a.shape}")
    #print(tk_a.head(5))
    #tk_a.to_csv(f"temp_data/tk_a_{gps_epoch}_distance.csv")

    #4. Compute radius (r)
    # [REMOVE before Package Release]
    #print(f"=====")
    #print(f"[DEBUG] Computing radius for gps_lat: {gps_lat}")
    #print(f"=====")
    
    tk_a['r'] = Kradius(gps_lat)
    # [REMOVE before Package Release]
    #print(f"[DEBUG] tk_a after Computing radius schema and shape: {tk_a.shape}")
    #print(tk_a.head(5))
    #tk_a.to_csv(f"temp_data/tk_a_{gps_epoch}_radius.csv")
    tk_b['r'] = Kradius(gps_lat)
    tk_c['r'] = Kradius(gps_lat)
    
   
    # [REMOVE before Package Release]
    #print(f"=====")
    #print(f"[DEBUG] Filtering rows that only fall into the computed R value")
    #print(f"=====")
    
    #5. Filtering rows that only fall into the computed R value.
    k_a = tk_a[tk_a['distance'] <= tk_a['r']]
    k_b = tk_b[tk_b['distance'] <= tk_b['r']]
    k_c = tk_c[tk_c['distance'] <= tk_c['r']]
    # [REMOVE before Package Release]
    #print(f"[DEBUG] filtered data  after space filter: {k_a.shape}")
    #k_a.to_csv(f"temp_data/k_a_{gps_epoch}.csv")
    #print(f"[DEBUG] k_b shape after space filter: {k_b.shape}")
    #k_b.to_csv(f"temp_data/k_b_{gps_epoch}.csv")
    #print(f"[DEBUG] k_c shape after space filter: {k_c.shape}")
    #k_c.to_csv(f"temp_data/k_c_{gps_epoch}.csv")
    #print(f"[DEBUG] tk_a distances: {tk_a['distance'].describe()}")
    #print(f"[DEBUG] tk_a radius: {tk_a['r'].iloc[0] if not tk_a.empty else 'N/A'}")

    #6. Quality filtering, Filtering Bad Points, using quality flags
    def filter_flags(df):
        df = df[df['F_res'].between(-2000, 2000)]
        df = df[df['Flags_F'].between(0, 1)]
        df = df[df['Flags_B'].between(0, 1)]
        return df
    
    # [REMOVE before Package Release]
    #print(f"[DEBUG] k_a before quality filter: {k_a.shape}")
    #print(f"[DEBUG] k_b before quality filter: {k_b.shape}")
    #print(f"[DEBUG] k_c before quality filter: {k_c.shape}")
    
    k_a = filter_flags(k_a)
    k_b = filter_flags(k_b)
    k_c = filter_flags(k_c)

    # [REMOVE before Package Release]
    #print(f"[DEBUG] k_a shape after quality filter: {k_a.shape}")
    #k_a.to_csv(f"temp_data/k_a_quality_{gps_epoch}.csv")
    #print(f"[DEBUG] k_b shape after quality filter: {k_b.shape}")
    #print(k_b.head())
    #k_b.to_csv(f"temp_data/k_b_quality_{gps_epoch}.csv")
    #print(f"[DEBUG] k_c shape after quality filter: {k_c.shape}")
    #print(k_c.head())
    #k_c.to_csv(f"temp_data/k_c_quality_{gps_epoch}.csv")

    #7.Combining the three satellited measures into a bigger dataframe that store all the Swarm points that were filtered. 
    swarm_filtered = pd.concat([k_a, k_b, k_c], keys=['A', 'B', 'C'], sort=False)
    
    # [REMOVE before Package Release]
    #print(f"[DEBUG] swarm_filtered_combined_ABC shape: {swarm_filtered.shape}")
    #print(swarm_filtered.head(5))
    
    #8.  Computing the minimum and average distance and the Kp index average.
    min_dist = swarm_filtered['distance'].min()
    avg_dist = swarm_filtered['distance'].mean()
    kp_avg = swarm_filtered['Kp'].mean()

    # [REMOVE before Package Release]
    #swarm_filtered.to_csv(f"temp_data/swarm_filtered_{gps_epoch}.csv")
    #print(f"=====")
    #print(f"[DEBUG] swarm_filtered shape: {swarm_filtered.shape}")
    #print(swarm_filtered.head(5))
    #print(f"=====")

    #8. Compute weights - Computing the d (hypotenuse computed from the edges ds, dt values
    ds = swarm_filtered['distance']
    r = swarm_filtered['r']
    dt = swarm_filtered['dT']
    swarm_filtered['Dj'] = DistJ(ds, r, dt, dt_seconds)
    swarm_filtered['W'] = 1 / (swarm_filtered['Dj'] ** 2)
    
    # [REMOVE before Package Release]
    #print(f"[DEBUG] swarm_filtered after Dj and W computation values: {swarm_filtered.shape}")
    #print(swarm_filtered.head(5))
    #swarm_filtered.to_csv(f"temp_data/swarm_filtered_{gps_epoch}_weights.csv")
    #print(f"=====")

    #9. Computing the Sum of weights    
    sum_w = swarm_filtered['W'].sum()
    #10. Distribution of weights
    swarm_filtered['Wj'] = swarm_filtered['W'] / sum_w

    # [REMOVE before Package Release]
    #print(f"=====")
    #print(f"[DEBUG] Weights sum: {sum_w}, Points: {len(swarm_filtered)}")
    #print(swarm_filtered[['distance', 'r', 'dT', 'Dj', 'W', 'Wj', 'N_res', 'E_res', 'C_res']].head())
    #print(f"=====")

    #9. Weighted interpolation - Computing the Magnetic component based on the weights previous weights. 
    n_res = (swarm_filtered['Wj'] * swarm_filtered['N_res']).sum()
    e_res = (swarm_filtered['Wj'] * swarm_filtered['E_res']).sum()
    c_res = (swarm_filtered['Wj'] * swarm_filtered['C_res']).sum()
    
    # [REMOVE before Package Release]
    #print(f"=====")
    #print(f"[DEBUG] Final part Interpolated N_res: {n_res}, E_res: {e_res}, C_res: {c_res}")
    #print(f"=====")
    
    #15. Write the results into an array that will be a dictionary for the final dataframe.
    return {
        'Latitude': gps_lat,
        'Longitude': gps_long,
        'Altitude': gps_altitude,
        'DateTime': gps_datetime,
        'N_res': n_res,
        'E_res': e_res,
        'C_res': c_res,
        'TotalPoints': len(swarm_filtered),  #Calculating the number of points per satellite that have passed the Space and Time Kernels.
        'Minimum_Distance': min_dist,
        'Average_Distance': avg_dist,
        'Kp': kp_avg
    }

