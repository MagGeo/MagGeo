import os
import pandas as pd
from maggeo.core import annotate_gps_with_geomag
from maggeo.date_utils import identify_unique_dates
from maggeo.gps import get_gps_data

def test_identify_unique_dates():
    """Test the identify_unique_dates function with sample GPS data."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    # Load GPS data first
    gps_df = get_gps_data(
        data_dir=data_dir,
        gpsfilename="trajectory_test.csv",
        lat_col="location-lat",
        lon_col="location-long",
        datetime_col="timestamp",
        altitude_col="height"
    )
    
    # Test unique dates identification
    unique_dates_df = identify_unique_dates(gps_df)
    
    # Assertions
    assert not unique_dates_df.empty, "Unique dates DataFrame should not be empty"
    assert 'date' in unique_dates_df.columns, "Should contain 'date' column"
    assert 'is_buffer_date' in unique_dates_df.columns, "Should contain 'is_buffer_date' column"
    assert 'buffer_type' in unique_dates_df.columns, "Should contain 'buffer_type' column"
    assert 'original_date' in unique_dates_df.columns, "Should contain 'original_date' column"
    
    # Check that dates are sorted
    assert unique_dates_df['date'].is_monotonic_increasing, "Dates should be sorted in ascending order"
    
    # Check that we have at least the original GPS dates
    original_dates = set(gps_df['dates'].unique())
    result_dates = set(unique_dates_df['date'])
    assert original_dates.issubset(result_dates), "All original GPS dates should be included"
    
    print(f"Successfully identified {len(unique_dates_df)} unique dates from GPS trajectory")
    print(f"Buffer dates added: {unique_dates_df['is_buffer_date'].sum()}")

def test_full_pipeline():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    params = {
        "data_dir": data_dir,
        "gpsfilename": "trajectory_test.csv",
        "lat_col": "location-lat",
        "long_col": "location-long",
        "datetime_col": "timestamp",
        "altitude_col": "height",
        "token": "3b5qyp3aNoVB9FEBEnKgrePoQtQhMUD-"
    }
    result_df = annotate_gps_with_geomag(params)
    assert not result_df.empty
    # Optionally, compare with expected output
    expected = pd.read_csv(os.path.join(data_dir, "expected_trajectory_test_output.csv"))
    pd.testing.assert_frame_equal(result_df.reset_index(drop=True), expected.reset_index(drop=True), check_dtype=False)