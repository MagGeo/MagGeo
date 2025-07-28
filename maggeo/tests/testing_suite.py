"""
Comprehensive testing suite for MagGeo library
Run with: pytest tests/ -v --cov=maggeo
"""

import pytest
import pandas as pd
import numpy as np
import datetime as dt
from pathlib import Path
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

# Import MagGeo components
from maggeo.core.processor import MagGeoProcessor, MagGeoConfig, process_gps_trajectory
from maggeo.core.exceptions import MagGeoError, ValidationError, SwarmDataError
from maggeo.core.swarm_client import SwarmClient
from maggeo.utils.validation import validate_gps_data, validate_config


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_gps_data():
    """Generate realistic GPS trajectory data for testing"""
    n_points = 50
    
    # Create a realistic trajectory (e.g., flight path over UK)
    base_lat = 55.0  # Scotland
    base_lon = -3.0
    
    return pd.DataFrame({
        'Latitude': np.random.normal(base_lat, 0.5, n_points),
        'Longitude': np.random.normal(base_lon, 0.5, n_points),
        'DateTime': pd.date_range('2023-06-01 10:00:00', periods=n_points, freq='1min'),
        'Altitude': np.random.uniform(0, 10000, n_points)  # Altitude in meters
    })

@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return MagGeoConfig(
        token="test_token_12345",
        lat_column="Latitude",
        lon_column="Longitude",
        datetime_column="DateTime",
        altitude_column="Altitude",
        max_workers=2,
        chunk_size=10
    )

@pytest.fixture
def mock_swarm_data():
    """Mock Swarm satellite data"""
    n_points = 1000
    base_time = dt.datetime(2023, 6, 1, 10, 0, 0)
    
    def create_satellite_data(satellite_id):
        return pd.DataFrame({
            'timestamp': pd.date_range(base_time, periods=n_points, freq='10s'),
            'epoch': range(n_points),
            'Latitude': np.random.uniform(50, 60, n_points),
            'Longitude': np.random.uniform(-10, 5, n_points),
            'Radius': np.random.uniform(6700000, 6800000, n_points),
            'B_N_res': np.random.normal(0, 100, n_points),
            'B_E_res': np.random.normal(0, 100, n_points),
            'B_C_res': np.random.normal(0, 150, n_points),
            'Satellite': satellite_id
        })
    
    return {
        'A': create_satellite_data('A'),
        'B': create_satellite_data('B'),
        'C': create_satellite_data('C')
    }

# ============================================================================
# UNIT TESTS - Core Processor
# ============================================================================

class TestMagGeoProcessor:
    """Test the main MagGeoProcessor class"""
    
    def test_processor_initialization(self, sample_config):
        """Test that processor initializes correctly"""
        processor = MagGeoProcessor(sample_config)
        
        assert processor.config == sample_config
        assert processor.swarm_client is not None
        assert processor.interpolator is not None
        assert processor.chaos_model is not None
    
    def test_load_gps_data_from_file(self, sample_config, sample_gps_data, tmp_path):
        """Test loading GPS data from CSV file"""
        # Save test data to temporary file
        test_file = tmp_path / "test_gps.csv"
        sample_gps_data.to_csv(test_file, index=False)
        
        processor = MagGeoProcessor(sample_config)
        loaded_data = processor._load_gps_data(test_file)
        
        assert len(loaded_data) == len(sample_gps_data)
        assert 'DateTime' in loaded_data.columns
        assert pd.api.types.is_datetime64_any_dtype(loaded_data['DateTime'])
    
    def test_load_gps_data_file_not_found(self, sample_config):
        """Test error handling when GPS file doesn't exist"""
        processor = MagGeoProcessor(sample_config)
        
        with pytest.raises(ValidationError, match="GPS file not found"):
            processor._load_gps_data("nonexistent_file.csv")
    
    def test_extract_unique_dates(self, sample_config, sample_gps_data):
        """Test extraction of unique dates with boundary conditions"""
        processor = MagGeoProcessor(sample_config)
        
        # Add some edge cases
        edge_data = sample_gps_data.copy()
        edge_data.loc[0, 'DateTime'] = pd.Timestamp('2023-06-01 02:30:00')  # Early morning
        edge_data.loc[1, 'DateTime'] = pd.Timestamp('2023-06-01 22:15:00')  # Late evening
        
        unique_dates = processor._extract_unique_dates(edge_data)
        
        assert len(unique_dates) >= 1
        assert isinstance(unique_dates[0], dt.date)
        
        # Should include previous day for early morning point
        assert dt.date(2023, 5, 31) in unique_dates
        # Should include next day for late evening point  
        assert dt.date(2023, 6, 2) in unique_dates
    
    @patch('maggeo.core.processor.SwarmClient')
    def test_fetch_swarm_data_parallel(self, mock_swarm_client, sample_config, mock_swarm_data):
        """Test parallel fetching of Swarm data"""
        # Setup mock
        mock_client_instance = Mock()
        mock_client_instance.get_residuals.return_value = (
            mock_swarm_data['A'], 
            mock_swarm_data['B'], 
            mock_swarm_data['C']
        )
        mock_swarm_client.return_value = mock_client_instance
        
        processor = MagGeoProcessor(sample_config)
        dates = [dt.date(2023, 6, 1), dt.date(2023, 6, 2)]
        
        swarm_data = processor._fetch_swarm_data_parallel(dates)
        
        assert 'A' in swarm_data
        assert 'B' in swarm_data  
        assert 'C' in swarm_data
        assert len(swarm_data['A']) > 0
    
    def test_calculate_magnetic_components(self, sample_config):
        """Test calculation of derived magnetic components"""
        processor = MagGeoProcessor(sample_config)
        
        # Create test data with known values
        test_data = pd.DataFrame({
            'N': [100.0, 200.0, -100.0],
            'E': [0.0, 100.0, 173.2],  # E component
            'C': [50.0, 150.0, 0.0]    # C component
        })
        
        result = processor._calculate_magnetic_components(test_data)
        
        # Test horizontal intensity H = sqrt(N² + E²)
        expected_h = np.sqrt(test_data['N']**2 + test_data['E']**2)
        np.testing.assert_array_almost_equal(result['H'], expected_h, decimal=2)
        
        # Test total intensity F = sqrt(N² + E² + C²)
        expected_f = np.sqrt(test_data['N']**2 + test_data['E']**2 + test_data['C']**2)
        np.testing.assert_array_almost_equal(result['F'], expected_f, decimal=2)
        
        # Test declination D = arctan2(E, N) in degrees
        expected_d = np.degrees(np.arctan2(test_data['E'], test_data['N']))
        np.testing.assert_array_almost_equal(result['D'], expected_d, decimal=2)


# ============================================================================
# UNIT TESTS - Swarm Client
# ============================================================================

class TestSwarmClient:
    """Test the SwarmClient class"""
    
    def test_swarm_client_initialization(self):
        """Test Swarm client initialization"""
        with patch('maggeo.core.swarm_client.set_token') as mock_set_token:
            client = SwarmClient("test_token")
            mock_set_token.assert_called_once_with(token="test_token")
            assert client.token == "test_token"
    
    @patch('maggeo.core.swarm_client.SwarmRequest')
    def test_get_residuals_success(self, mock_swarm_request):
        """Test successful Swarm data retrieval"""
        # Setup mock response
        mock_request_instance = Mock()
        mock_data = Mock()
        mock_df = pd.DataFrame({
            'Latitude': [55.0, 55.1],
            'Longitude': [-3.0, -3.1], 
            'Radius': [6700000, 6700100],
            'B_NEC': [[100, 50, 150], [102, 52, 148]],
            'B_NEC_res_CHAOS-Core': [[10, 5, 15], [12, 7, 13]],
            'QDLat': [60.0, 60.1],
            'QDLon': [45.0, 45.1],
            'MLT': [12.0, 12.1]
        }, index=pd.date_range('2023-06-01', periods=2, freq='1min'))
        
        mock_data.as_dataframe.return_value = mock_df
        mock_request_instance.get_between.return_value = mock_data
        mock_swarm_request.return_value = mock_request_instance
        
        client = SwarmClient("test_token")
        start_time = dt.datetime(2023, 6, 1, 10, 0, 0)
        end_time = dt.datetime(2023, 6, 1, 11, 0, 0)
        
        data_a, data_b, data_c = client.get_residuals(start_time, end_time)
        
        # Verify that data was processed for all satellites
        assert len(data_a) > 0
        assert len(data_b) > 0  
        assert len(data_c) > 0
        
        # Check that processed data has expected columns
        expected_columns = ['timestamp', 'Latitude', 'Longitude', 'B_N_res', 'B_E_res', 'B_C_res']
        for col in expected_columns:
            assert col in data_a.columns


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestMagGeoIntegration:
    """Integration tests for the complete MagGeo pipeline"""
    
    @patch('maggeo.core.swarm_client.SwarmRequest')
    @patch('maggeo.core.chaos_model.CHAOSModel.get_ground_values')
    @patch('maggeo.core.interpolation.MagneticFieldInterpolator.interpolate_point')
    def test_full_processing_pipeline(self, mock_interpolate, mock_chaos, mock_swarm_request, 
                                    sample_config, sample_gps_data):
        """Test the complete processing pipeline end-to-end"""
        
        # Setup mocks
        mock_swarm_request.return_value.get_between.return_value.as_dataframe.return_value = pd.DataFrame({
            'Latitude': [55.0], 'Longitude': [-3.0], 'Radius': [6700000],
            'B_NEC': [[100, 50, 150]], 'B_NEC_res_CHAOS-Core': [[10, 5, 15]],
            'QDLat': [60.0], 'QDLon': [45.0], 'MLT': [12.0]
        }, index=[dt.datetime(2023, 6, 1, 10, 0, 0)])
        
        mock_interpolate.return_value = {
            'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': 1000.0,
            'DateTime': dt.datetime(2023, 6, 1, 10, 0, 0),
            'N_res': 10.0, 'E_res': 5.0, 'C_res': 15.0,
            'TotalPoints': 5, 'Minimum_Distance': 100.0, 'Average_Distance': 200.0
        }
        
        mock_chaos.return_value = {
            'N': [20000.0], 'E': [1000.0], 'C': [45000.0],
            'N_internal': [19000.0], 'E_internal': [900.0], 'C_internal': [44000.0]
        }
        
        # Run processing
        processor = MagGeoProcessor(sample_config)
        result = processor.process_trajectory(sample_gps_data.head(1))  # Process just 1 point
        
        # Verify results
        assert len(result) == 1
        assert 'H' in result.columns  # Horizontal intensity
        assert 'D' in result.columns  # Declination
        assert 'I' in result.columns  # Inclination
        assert 'F' in result.columns  # Total intensity
        
        # Verify calculations are reasonable
        assert result['H'].iloc[0] > 0
        assert result['F'].iloc[0] > result['H'].iloc[0]  # Total > Horizontal


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test input data validation functions"""
    
    def test_validate_gps_data_success(self, sample_config, sample_gps_data):
        """Test successful GPS data validation"""
        # Should not raise any exceptions
        validate_gps_data(sample_gps_data, sample_config)
    
    def test_validate_gps_data_missing_columns(self, sample_config):
        """Test GPS data validation with missing required columns"""
        invalid_data = pd.DataFrame({
            'Latitude': [55.0, 55.1],
            'Longitude': [-3.0, -3.1]
            # Missing DateTime and Altitude columns
        })
        
        with pytest.raises(ValidationError, match="Missing required column"):
            validate_gps_data(invalid_data, sample_config)
    
    def test_validate_gps_data_invalid_coordinates(self, sample_config):
        """Test GPS data validation with invalid coordinates"""
        invalid_data = pd.DataFrame({
            'Latitude': [95.0, -95.0],  # Invalid latitudes
            'Longitude': [185.0, -185.0],  # Invalid longitudes
            'DateTime': pd.date_range('2023-06-01', periods=2),
            'Altitude': [1000, 2000]
        })
        
        with pytest.raises(ValidationError, match="Invalid coordinate"):
            validate_gps_data(invalid_data, sample_config)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance and memory usage tests"""
    
    def test_large_dataset_processing(self, sample_config):
        """Test processing of larger GPS datasets"""
        # Create larger test dataset
        large_gps_data = pd.DataFrame({
            'Latitude': np.random.uniform(50, 60, 1000),
            'Longitude': np.random.uniform(-10, 5, 1000),
            'DateTime': pd.date_range('2023-06-01', periods=1000, freq='1min'),
            'Altitude': np.random.uniform(0, 10000, 1000)
        })
        
        # This test mainly checks that processing doesn't crash with larger datasets
        # In a real scenario, you'd want to measure actual processing time
        processor = MagGeoProcessor(sample_config)
        
        # Test date extraction (should be fast)
        import time
        start_time = time.time()
        unique_dates = processor._extract_unique_dates(large_gps_data)
        duration = time.time() - start_time
        
        assert duration < 1.0  # Should complete within 1 second
        assert len(unique_dates) > 0
    
    def test_memory_usage_chunked_processing(self, sample_config, sample_gps_data):
        """Test that chunked processing doesn't cause memory issues"""
        processor = MagGeoProcessor(sample_config)
        processor.config.chunk_size = 5  # Small chunks for testing
        
        # Create mock swarm data
        mock_swarm_data = {
            'A': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
            'B': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
            'C': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]})
        }
        
        # This should process without memory errors
        try:
            with patch.object(processor.interpolator, 'interpolate_point') as mock_interp:
                mock_interp.return_value = {
                    'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': 1000.0,
                    'DateTime': dt.datetime.now(), 'N_res': 0, 'E_res': 0, 'C_res': 0,
                    'TotalPoints': 1, 'Minimum_Distance': 100, 'Average_Distance': 200
                }
                result = processor._interpolate_magnetic_fields(sample_gps_data, mock_swarm_data)
                assert len(result) == len(sample_gps_data)
        except MemoryError:
            pytest.fail("Chunked processing caused memory error")


# ============================================================================
# CLI TESTS
# ============================================================================

class TestCLI:
    """Test command-line interface"""
    
    def test_cli_help(self):
        """Test that CLI help works"""
        from click.testing import CliRunner
        from maggeo.cli.main import main
        
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert 'Usage:' in result.output
    
    def test_cli_missing_token(self, tmp_path):
        """Test CLI error handling when token is missing"""
        from click.testing import CliRunner
        from maggeo.cli.main import main
        
        # Create dummy config file
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
        maggeo:
          gpsfilename: "test.csv"
          Lat: "Latitude"
          Long: "Longitude"
          DateTime: "DateTime"
          altitude: "Altitude"
        """)
        
        runner = CliRunner()
        result = runner.invoke(main, ['-p', str(config_file)])
        
        # Should fail without token
        assert result.exit_code != 0


# ============================================================================
# DOCUMENTATION TESTS
# ============================================================================

def test_quarto_documentation_build():
    """Test that Quarto documentation builds successfully"""
    import subprocess
    from pathlib import Path
    
    # Skip if not in development environment
    docs_dir = Path("docs")
    if not docs_dir.exists():
        pytest.skip("Documentation directory not found")
    
    # Check if quarto is available
    try:
        subprocess.run(["quarto", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("Quarto not available")
    
    # Test Quarto build
    result = subprocess.run(
        ["quarto", "render", str(docs_dir)],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Quarto build failed: {result.stderr}"
    
    # Check that HTML files were generated
    output_dir = docs_dir / "_site"
    if output_dir.exists():
        html_files = list(output_dir.glob("**/*.html"))
        assert len(html_files) > 0, "No HTML files generated"


def test_example_notebooks():
    """Test that example Jupyter notebooks run without errors"""
    import subprocess
    from pathlib import Path
    
    examples_dir = Path("examples")
    if not examples_dir.exists():
        pytest.skip("Examples directory not found")
    
    notebooks = list(examples_dir.glob("*.ipynb"))
    if not notebooks:
        pytest.skip("No example notebooks found")
    
    for notebook in notebooks:
        # Test notebook execution
        result = subprocess.run([
            "jupyter", "nbconvert", 
            "--execute", 
            "--to", "notebook",
            "--output", f"{notebook.stem}_test.ipynb",
            str(notebook)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Notebook {notebook} failed: {result.stderr}"
        
        # Clean up test output
        test_output = notebook.parent / f"{notebook.stem}_test.ipynb"
        if test_output.exists():
            test_output.unlink()


# ============================================================================
# CONFTEST - Additional test configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "docs: marks tests as documentation tests"
    )