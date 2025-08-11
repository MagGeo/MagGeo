import os
import pandas as pd
from maggeo.gps import get_gps_data

def test_get_gps_data_basic():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    df = get_gps_data(
        data_dir=data_dir,
        gpsfilename="trajectory_test.csv",
        lat_col="location-lat",
        lon_col="location-long",
        datetime_col="timestamp",
        altitude_col="height"
    )
    assert not df.empty
    assert all(col in df.columns for col in ["gpsLat", "gpsLong", "gpsDateTime", "gpsAltitude"])
    assert df["gpsAltitude"].min() >= 0