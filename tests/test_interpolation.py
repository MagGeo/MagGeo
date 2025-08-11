import pandas as pd
from maggeo.interpolation import st_idw_process

def test_st_idw_process():
    # Prepare GPS data with correct types
    gps_data = [
        {
            "gpsLat": float(70.8303),
            "gpsLong": float(67.97505),
            "gpsAltitude": float(0.406),
            "gpsDateTime": pd.Timestamp("2014-09-08 06:10:00"), 
            "epoch": int(1410156600),
            "dates": pd.to_datetime("2014-09-08").date(),
            "times": pd.to_datetime("06:10:00", format="%H:%M:%S").time()
        }
    ]
    df = pd.DataFrame(gps_data)

    # Read Swarm data from external CSVs as required by the pipeline
    swarm_a = pd.read_csv("tests/data/swarm_Concat_A.csv")
    swarm_b = pd.read_csv("tests/data/swarm_Concat_B.csv")
    swarm_c = pd.read_csv("tests/data/swarm_Concat_C.csv")
    # Ensure the 'epoch' column is in the correct format for indexing
    swarm_a.set_index('epoch', inplace=True)
    swarm_b.set_index('epoch', inplace=True)
    swarm_c.set_index('epoch', inplace=True)

    # Use the first (and so far the only) row for the test
    row = df.iloc[0]
    result = st_idw_process(
        gps_lat=row["gpsLat"],
        gps_long=row["gpsLong"],
        gps_altitude=row["gpsAltitude"],
        gps_datetime=row["gpsDateTime"],
        gps_epoch=row["epoch"],
        swarm_a=swarm_a,
        swarm_b=swarm_b,
        swarm_c=swarm_c
    )
    assert isinstance(result, dict)
    assert "N_res" in result and "E_res" in result and "C_res"