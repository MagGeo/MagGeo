import pandas as pd
from maggeo.swarm import get_swarm_residuals
from datetime import datetime

def test_get_swarm_residuals(monkeypatch):
    # Use a short, fixed date range for testing
    start = pd.Timestamp("2014-09-07 00:00:00")
    end = pd.Timestamp("2014-09-07 23:59:59")
    token = "3b5qyp3aNoVB9FEBEnKgrePoQtQhMUD-"  # Use a valid token or mock SwarmRequest for CI
    a, b, c = get_swarm_residuals(start, end, token)
    assert isinstance(a, pd.DataFrame)
    assert isinstance(b, pd.DataFrame)
    assert isinstance(c, pd.DataFrame)