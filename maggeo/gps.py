# 0. Get the GPS track in a CSV format.
# Input: csv file store in the data folder, validate if there is a altitude attribute.
# Output: GPS Data as pandas DF.
import os
import pandas as pd

def get_gps_data(
        data_dir,
        gpsfilename,
        lat_col,
        lon_col,
        datetime_col,
        altitude_col='',
        return_original_cols=False
    ) -> pd.DataFrame:
    """Get GPS data from a CSV file and return it as a pandas DataFrame.
    This function reads a CSV file containing GPS data, renames the columns to standard names,
    and ensures that the altitude column is present. If the altitude column is not provided,
    it defaults to an empty string and sets the altitude to 0 for all entries.
    If the altitude is not provided, it will be set to 0 for all entries.

    Parameters
    ----------
    data_dir : str
        Directory where the GPS data CSV file is located.
    gpsfilename : str
        Name of the GPS data CSV file.
    lat_col : str
        Name of the column containing latitude data.
    lon_col : str
        Name of the column containing longitude data.
    datetime_col : str
        Name of the column containing date and time data.
    altitude_col : str
        Name of the column containing altitude data. If not provided, defaults to an empty string.
        If altitude is not provided, it will be set to 0 for all entries
    return_original_cols : bool, optional
        If True, also return the original DataFrame as read from CSV (default False).

    Returns
    -------
    pd.DataFrame
        DataFrame containing the GPS data with columns renamed to 'gpsLat', 'gpsLong',
        'gpsDateTime', and 'gpsAltitude'. If altitude is not provided, 'gpsAltitude' will be set to 0 for all entries.
    """
    # Read the original CSV file without any modifications
    original_nfp = pd.read_csv(os.path.join(data_dir, gpsfilename), encoding='utf-8', dayfirst=True)

    # Check if altitude is provided, if not, set it to an empty string
    if not altitude_col:
        nfp = pd.read_csv(
            os.path.join(data_dir, gpsfilename),
            parse_dates=[0], encoding='utf-8', dayfirst=True,
            usecols=[lat_col, lon_col, datetime_col]
        )
        nfp['gpsAltitude'] = 0
        rename_dict = {lat_col: 'gpsLat', lon_col: 'gpsLong', datetime_col: 'gpsDateTime'}
    else:
        # If altitude is provided, read it from the CSV file (include altitude_col in usecols)
        nfp = pd.read_csv(
            os.path.join(data_dir, gpsfilename),
            parse_dates=[0], encoding='utf-8', dayfirst=True,
            usecols=[lat_col, lon_col, datetime_col, altitude_col]
        )
        nfp.loc[(nfp[altitude_col] < 0) | (nfp[altitude_col].isnull()), altitude_col] = 0
        rename_dict = {lat_col: 'gpsLat', lon_col: 'gpsLong', datetime_col: 'gpsDateTime', altitude_col: 'gpsAltitude'}

    nfp.rename(columns=rename_dict, inplace=True)
    # Convert the gpsDateTime to datetime python object
    nfp['gpsDateTime'] = pd.to_datetime(nfp['gpsDateTime'])
    nfp['gpsDateTime'] = nfp['gpsDateTime'].map(lambda x: x.replace(second=0))
    nfp['gpsLat'] = nfp['gpsLat'].astype(float)
    nfp['gpsLong'] = nfp['gpsLong'].astype(float)
    # Adding new column epoch, will be useful to compare the date&time o each gps point against the gathered Swarm data points
    #nfp['epoch'] = nfp['gpsDateTime'].view('int64') // 1_000_000_000
    nfp['epoch'] = nfp['gpsDateTime'].astype('int64') // 1e9
    nfp['epoch'] = nfp['epoch'].astype(int)
    # Computing Date and Time columns
    nfp['dates'] = nfp['gpsDateTime'].dt.date
    nfp['times'] = nfp['gpsDateTime'].dt.time

    if return_original_cols:
        # Return the original DataFrame as well
        return original_nfp.copy()

    return nfp
