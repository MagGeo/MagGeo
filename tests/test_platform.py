import os
import platform
import pytest
from pathlib import Path

def test_cross_platform_paths():
    """Test that file paths work correctly across platforms."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    test_file = os.path.join(data_dir, "trajectory_test.csv")
    
    # Test that the file exists using both approaches
    assert os.path.exists(test_file), f"Test file not found: {test_file}"
    
    # Test Path object approach (more modern)
    test_path = Path(__file__).parent / "data" / "trajectory_test.csv"
    assert test_path.exists(), f"Test file not found using Path: {test_path}"
    
    # Log platform info for debugging
    print(f"Platform: {platform.system()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Test file path: {test_file}")

@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
def test_windows_specific_features():
    """Test Windows-specific functionality if needed."""
    # This test only runs on Windows
    assert platform.system() == "Windows"
    
    # Test that we can handle Windows paths correctly
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    # On Windows, paths might use backslashes
    normalized_path = os.path.normpath(data_dir)
    assert os.path.exists(normalized_path)
