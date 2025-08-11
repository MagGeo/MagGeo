"""
Tests for the date_utils module.
"""

import os
import pandas as pd
import datetime as dt
from maggeo.date_utils import identify_unique_dates


def test_identify_unique_dates_basic():
    """Test basic functionality of identify_unique_dates."""
    # Create simple test data
    test_data = {
        'dates': [
            pd.Timestamp('2023-01-01').date(),
            pd.Timestamp('2023-01-01').date(),
            pd.Timestamp('2023-01-02').date(),
        ],
        'times': [
            dt.time(2, 30, 0),   # Early morning - should add buffer
            dt.time(14, 30, 0),  # Afternoon - no buffer
            dt.time(21, 30, 0),  # Late evening - should add buffer
        ]
    }
    gps_df = pd.DataFrame(test_data)
    
    result = identify_unique_dates(gps_df)
    
    # Should have 4 dates: 2 original + 2 buffer dates
    assert len(result) == 4
    assert 'date' in result.columns
    assert 'is_buffer_date' in result.columns
    assert 'buffer_type' in result.columns
    assert 'original_date' in result.columns
    
    # Check buffer dates are correctly identified
    buffer_dates = result[result['is_buffer_date']]
    assert len(buffer_dates) == 2
    assert 'early_morning' in buffer_dates['buffer_type'].values
    assert 'late_evening' in buffer_dates['buffer_type'].values


if __name__ == "__main__":
    test_identify_unique_dates_basic()
    print("✓ All date_utils tests passed!")
