import pandas as pd
from maggeo.chaos import chaos_ground_values
import numpy as np

def test_chaos_ground_values():
    """Test chaos_ground_values with a single row DataFrame containing geospatial and datetime data."""
    data = [
    {
        "Latitude": 70.8303,
        "Longitude": 67.97505,
        "Altitude": 0.406,
        "DateTime": "2014-09-08 05:54:00",
        "N_res": -13.975720388396816,
        "E_res": 10.237463326390095,
        "C_res": -0.2564250319988548
    }
    ]
    df = pd.DataFrame(data)
    df["DateTime"] = pd.to_datetime(df["DateTime"])

    X_obs = [6989.983482]
    Y_obs = [3866.523497]
    Z_obs= [57646.924881]
    X_obs_internal = [7009.42559296]
    Y_obs_internal = [3854.00170347]
    Z_obs_internal = [57636.83205246]
    # Call the chaos_ground_values function
    # This function should return the computed magnetic field components in the geodetic frame
    # based on the input DataFrame.
    # For example:
    # X, Y, Z, X_int, Y_int, Z_int = chaos_ground_values(df)
    # assert X == X_obs and Y == Y_obs and Z == Z_obs
    # assert X_int == X_obs_internal and Y_int == Y_obs_internal and Z_int == Z_obs_internal
    # For this test, we will directly check the expected values.

    X, Y, Z, X_int, Y_int, Z_int = chaos_ground_values(df)
    assert len(X) == 1 and len(Y) == 1 and len(Z) == 1
    assert len(X_int) == 1 and len(Y_int) == 1 and len(Z_int) == 1

   
    assert np.allclose(X, X_obs), f"Expected X={X_obs}, got {X}"
    assert np.allclose(Y, Y_obs), f"Expected Y={Y_obs}, got {Y}"
    assert np.allclose(Z, Z_obs), f"Expected Z={Z_obs}, got {Z}"
    assert np.allclose(X_int, X_obs_internal), f"Expected X={X_obs_internal}, got {X_int}"
    assert np.allclose(Y_int, Y_obs_internal), f"Expected Y={Y_obs_internal}, got {Y_int}"
    assert np.allclose(Z_int, Z_obs_internal), f"Expected Z={Z_obs_internal}, got {Z_int}"

