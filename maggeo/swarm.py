# 1. For each day in the trajectory, Get the Swarm Data and Residuals: Get_Swarm_and_residuals
# Input:  Date and Time variables
# Output: Swarm DF for each Sat, including the residuals, and Quality Flags.

import os
from viresclient import SwarmRequest

# Global variable to track if token has been set to avoid multiple "Token saved" messages
_token_set = False

def get_swarm_residuals(startDateTime, endDateTime, token=None) -> tuple:
    """Request Swarm data and residuals for a specified time range.
    This function uses the Viresclient to request data from the Swarm mission for three satellites (A, B, C).

    Parameters
    ----------
    startDateTime : pd.Timestamp
        Start date and time for the data request.
    endDateTime : pd.Timestamp
        End date and time for the data request.
    token : str, optional
        VirES token for authentication. If provided, will be set before making requests.

    Returns
    -------
    tuple
        Tuple containing three pandas DataFrames for each Swarm satellite (A, B, C) with the requested data.
    """
    global _token_set
    
    # Set VirES token if provided and not already set
    if token and not _token_set:
        from viresclient import set_token
        set_token(token=token, set_default=True)
        _token_set = True
    elif not token and not _token_set:
        # Try to get token from environment variable
        env_token = os.environ.get('VIRES_TOKEN')
        if env_token:
            from viresclient import set_token
            set_token(token=env_token, set_default=True)
            _token_set = True

    # Display important package versions used
    # Edit this according to what you use
    #  - this will help others to reproduce your results
    #  - it may also help to trace issues if package changes break your code
 
    # Ensure the token is set for the Vires client    
    # Create SwarmRequest objects for each satellite
    # These objects will be used to request data from the Swarm mission
    # Each request will be configured to fetch specific data products and models
    
    requestA = SwarmRequest()
    requestB = SwarmRequest()
    requestC = SwarmRequest()
    

    ### 1. Request data for Sat Alpha
    requestA.set_collection("SW_OPER_MAGA_LR_1B")
    requestA.set_products(
        measurements=[
            'F', #Magnetic intensity
            'B_NEC', #The Magnetic values are in NEC system (North, East, Centre)
            'Flags_F', #Quality Flag to validate nominal values for ASM
            'Flags_B', #Quality Flag to validate nominal values for VFM, check here for more details https://earth.esa.int/web/guest/missions/esa-eo-missions/swarm/data-handbook/level-1b-product-definitions#label-Flag-Values-of-MDR_MAG_HR
        ],

        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        auxiliaries=['Kp'],
        residuals=True, #Brining the residuals.
        sampling_step="PT30S", #Get the data every 30 seconds. Trajectories often include timestamps at minute intervals
    )
   
    #2. Define an pandas dataframe to store the data request for Satellite A, based on the start Date and time.
    #You can display dsA to get an idea of how the data is requested.
    dsA = requestA.get_between(
        start_time=startDateTime,
        end_time=endDateTime, 
        show_progress = False,
        asynchronous = False
    ).as_dataframe(expand=True)
    ### End Request for Satellite Alpha
    
    ### 2. Request for Satellite Bravo, same request parameters defined by Satellite Alpha
    requestB.set_collection("SW_OPER_MAGB_LR_1B")
    requestB.set_products(
        measurements=[
            'F', #Magnetic intensity
            'B_NEC',
            'Flags_F',
            'Flags_B',

        ],
        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        auxiliaries=['Kp'],
        residuals=True, 
        sampling_step="PT30S",
    )

    dsB = requestB.get_between(
        start_time= startDateTime,
        end_time= endDateTime,
        show_progress = False,
        asynchronous = False
    ).as_dataframe(expand=True)
    ### End Request for Satellite Bravo
    
    ## 3. Request for Satellite Charlie.
    requestC.set_collection("SW_OPER_MAGC_LR_1B")
    requestC.set_products(
        measurements=[
            'F',
            'B_NEC',
            'Flags_F',
            'Flags_B',

        ],
        models = [
            
            '"CHAOS_MCO_MLI_MMA" = "CHAOS-Core" + "CHAOS-Static" + "CHAOS-MMA-Primary" + "CHAOS-MMA-Secondary"'
        ],
        auxiliaries=['Kp'],
        residuals=True,
        sampling_step="PT30S", # trajectories often include timestamps at minute intervals
        #sampling_step="PT60S", #Get the data every 60 seconds.
    )

    dsC = requestC.get_between(
        start_time=startDateTime,
        end_time=endDateTime,
        show_progress = False,
        asynchronous = False
    ).as_dataframe(expand=True) 
    ### End Request for Satellite Charlie
    
    ##4. Renaming Geomagnetic components columns.
    dsA.rename(columns={"F_res_CHAOS_MCO_MLI_MMA":"F_res","B_NEC_res_CHAOS_MCO_MLI_MMA_N": "N_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_E":"E_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_C":"C_res"}, inplace = True)
    dsB.rename(columns={"F_res_CHAOS_MCO_MLI_MMA":"F_res","B_NEC_res_CHAOS_MCO_MLI_MMA_N": "N_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_E":"E_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_C":"C_res"}, inplace = True)
    dsC.rename(columns={"F_res_CHAOS_MCO_MLI_MMA":"F_res","B_NEC_res_CHAOS_MCO_MLI_MMA_N": "N_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_E":"E_res", "B_NEC_res_CHAOS_MCO_MLI_MMA_C":"C_res"}, inplace = True)
    
    #5. Add the epoch column, and set that as the pandas Dataframe index. Useful to get an ID for each date and time.
    dsA['epoch'] = dsA.index
    dsA['timestamp'] = dsA.index
    dsA['epoch'] = (dsA['epoch'].astype('int64') // int(1e9)).astype(int)
    dsA.set_index("epoch", inplace=True)

    dsB['epoch'] = dsB.index
    dsB['timestamp'] = dsB.index
    dsB['epoch'] = (dsB['epoch'].astype('int64') // int(1e9)).astype(int)
    dsB.set_index("epoch", inplace=True)

    dsC['epoch'] = dsC.index
    dsC['timestamp'] = dsC.index
    dsC['epoch'] = (dsC['epoch'].astype('int64') // int(1e9)).astype(int)
    dsC.set_index("epoch", inplace=True)

    return dsA, dsB, dsC
