"""
Performance benchmarks for MagGeo library
Run with: pytest tests/performance/ --benchmark-only
"""

import pytest
import pandas as pd
import numpy as np
import datetime as dt
from unittest.mock import Mock, patch
import time
import memory_profiler
from pathlib import Path

from maggeo.core.processor import MagGeoProcessor, MagGeoConfig


class TestPerformanceBenchmarks:
    """Performance benchmarks for MagGeo components"""
    
    @pytest.fixture
    def benchmark_config(self):
        """Configuration for benchmarking"""
        return MagGeoConfig(
            token="benchmark_token",
            max_workers=4,
            chunk_size=100
        )
    
    def generate_gps_data(self, n_points: int) -> pd.DataFrame:
        """Generate synthetic GPS data for benchmarking"""
        return pd.DataFrame({
            'Latitude': np.random.uniform(50, 60, n_points),
            'Longitude': np.random.uniform(-10, 5, n_points),
            'DateTime': pd.date_range('2023-06-01 10:00:00', 
                                    periods=n_points, 
                                    freq='1min'),
            'Altitude': np.random.uniform(0, 10000, n_points)
        })
    
    def generate_swarm_data(self, n_points: int) -> dict:
        """Generate synthetic Swarm data for benchmarking"""
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
    
    # ========================================================================
    # GPS DATA PROCESSING BENCHMARKS
    # ========================================================================
    
    def test_gps_data_loading_small(self, benchmark, benchmark_config, tmp_path):
        """Benchmark GPS data loading - small dataset (100 points)"""
        gps_data = self.generate_gps_data(100)
        test_file = tmp_path / "test_gps_small.csv"
        gps_data.to_csv(test_file, index=False)
        
        processor = MagGeoProcessor(benchmark_config)
        
        result = benchmark(processor._load_gps_data, test_file)
        assert len(result) == 100
    
    def test_gps_data_loading_large(self, benchmark, benchmark_config, tmp_path):
        """Benchmark GPS data loading - large dataset (10,000 points)"""
        gps_data = self.generate_gps_data(10000)
        test_file = tmp_path / "test_gps_large.csv"
        gps_data.to_csv(test_file, index=False)
        
        processor = MagGeoProcessor(benchmark_config)
        
        result = benchmark(processor._load_gps_data, test_file)
        assert len(result) == 10000
    
    def test_date_extraction_performance(self, benchmark, benchmark_config):
        """Benchmark unique date extraction from GPS data"""
        gps_data = self.generate_gps_data(5000)
        processor = MagGeoProcessor(benchmark_config)
        
        result = benchmark(processor._extract_unique_dates, gps_data)
        assert len(result) > 0
    
    # ========================================================================
    # SWARM DATA PROCESSING BENCHMARKS  
    # ========================================================================
    
    @patch('maggeo.core.swarm_client.SwarmRequest')
    def test_swarm_data_fetching_single_date(self, mock_swarm_request, benchmark, benchmark_config):
        """Benchmark Swarm data fetching for single date"""
        # Mock Swarm response
        mock_data = Mock()
        mock_df = pd.DataFrame({
            'Latitude': np.random.uniform(50, 60, 1000),
            'Longitude': np.random.uniform(-10, 5, 1000),
            'Radius': np.random.uniform(6700000, 6800000, 1000),
            'B_NEC': [[100, 50, 150]] * 1000,
            'B_NEC_res_CHAOS-Core': [[10, 5, 15]] * 1000,
            'QDLat': np.random.uniform(55, 65, 1000),
            'QDLon': np.random.uniform(40, 50, 1000),
            'MLT': np.random.uniform(0, 24, 1000)
        }, index=pd.date_range('2023-06-01', periods=1000, freq='30s'))
        
        mock_data.as_dataframe.return_value = mock_df
        mock_swarm_request.return_value.get_between.return_value = mock_data
        
        processor = MagGeoProcessor(benchmark_config)
        test_date = dt.date(2023, 6, 1)
        
        result = benchmark(processor._fetch_swarm_data_for_date, test_date)
        assert len(result[0]) > 0  # Swarm A data
    
    def test_swarm_data_parallel_vs_sequential(self, benchmark_config):
        """Compare parallel vs sequential Swarm data fetching"""
        dates = [dt.date(2023, 6, 1) + dt.timedelta(days=i) for i in range(5)]
        
        # Mock the actual fetching to focus on parallelization overhead
        with patch.object(MagGeoProcessor, '_fetch_swarm_data_for_date') as mock_fetch:
            mock_fetch.return_value = (
                pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
                pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
                pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]})
            )
            
            processor = MagGeoProcessor(benchmark_config)
            
            # Benchmark parallel execution
            start_time = time.time()
            result_parallel = processor._fetch_swarm_data_parallel(dates)
            parallel_time = time.time() - start_time
            
            # Benchmark sequential execution (simulate)
            start_time = time.time()
            for date in dates:
                processor._fetch_swarm_data_for_date(date)
            sequential_time = time.time() - start_time
            
            print(f"Parallel: {parallel_time:.3f}s, Sequential: {sequential_time:.3f}s")
            print(f"Speedup: {sequential_time/parallel_time:.2f}x")
    
    # ========================================================================
    # INTERPOLATION BENCHMARKS
    # ========================================================================
    
    @patch('maggeo.core.interpolation.MagneticFieldInterpolator.interpolate_point')
    def test_interpolation_performance_chunked(self, mock_interpolate, benchmark, benchmark_config):
        """Benchmark chunked interpolation processing"""
        # Setup mock interpolation
        mock_interpolate.return_value = {
            'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': 1000.0,
            'DateTime': dt.datetime.now(), 'N_res': 10.0, 'E_res': 5.0, 'C_res': 15.0,
            'TotalPoints': 5, 'Minimum_Distance': 100.0, 'Average_Distance': 200.0
        }
        
        gps_data = self.generate_gps_data(1000)
        swarm_data = self.generate_swarm_data(5000)
        processor = MagGeoProcessor(benchmark_config)
        
        result = benchmark(processor._interpolate_magnetic_fields, gps_data, swarm_data)
        assert len(result) == 1000
    
    def test_chunk_size_optimization(self, benchmark_config):
        """Test optimal chunk size for interpolation"""
        gps_data = self.generate_gps_data(2000)
        swarm_data = self.generate_swarm_data(10000)
        
        chunk_sizes = [50, 100, 200, 500, 1000]
        results = {}
        
        with patch('maggeo.core.interpolation.MagneticFieldInterpolator.interpolate_point') as mock_interp:
    @memory_profiler.profile
    def test_memory_usage_large_dataset(self, benchmark_config):
        """Profile memory usage with large datasets"""
        # This test requires memory_profiler: pip install memory-profiler
        gps_data = self.generate_gps_data(5000)
        swarm_data = self.generate_swarm_data(50000)
        
        with patch('maggeo.core.interpolation.MagneticFieldInterpolator.interpolate_point') as mock_interp:
            mock_interp.return_value = {
                'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': 1000.0,
                'DateTime': dt.datetime.now(), 'N_res': 0, 'E_res': 0, 'C_res': 0,
                'TotalPoints': 1, 'Minimum_Distance': 100, 'Average_Distance': 200
            }
            
            processor = MagGeoProcessor(benchmark_config)
            
            # Process in chunks to monitor memory usage
            result = processor._interpolate_magnetic_fields(gps_data, swarm_data)
            assert len(result) == len(gps_data)
    
    def test_memory_efficiency_chunking(self):
        """Test that chunking reduces peak memory usage"""
        import psutil
        import os
        
        gps_data = self.generate_gps_data(2000)
        swarm_data = self.generate_swarm_data(20000)
        
        process = psutil.Process(os.getpid())
        
        # Test with large chunks (high memory usage)
        config_large = MagGeoConfig(token="test", chunk_size=2000)
        processor_large = MagGeoProcessor(config_large)
        
        with patch('maggeo.core.interpolation.MagneticFieldInterpolator.interpolate_point') as mock_interp:
            mock_interp.return_value = {
                'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': 1000.0,
                'DateTime': dt.datetime.now(), 'N_res': 0, 'E_res': 0, 'C_res': 0,
                'TotalPoints': 1, 'Minimum_Distance': 100, 'Average_Distance': 200
            }
            
            # Measure memory before
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process with large chunks
            processor_large._interpolate_magnetic_fields(gps_data, swarm_data)
            memory_large_chunk = process.memory_info().rss / 1024 / 1024  # MB
            
            # Test with small chunks (lower memory usage)
            config_small = MagGeoConfig(token="test", chunk_size=100)  
            processor_small = MagGeoProcessor(config_small)
            
            processor_small._interpolate_magnetic_fields(gps_data, swarm_data)
            memory_small_chunk = process.memory_info().rss / 1024 / 1024  # MB
            
            print(f"Memory usage - Before: {memory_before:.1f} MB")
            print(f"Memory usage - Large chunks: {memory_large_chunk:.1f} MB")
            print(f"Memory usage - Small chunks: {memory_small_chunk:.1f} MB")
            
            # Small chunks should use less peak memory
            assert memory_small_chunk <= memory_large_chunk * 1.1  # Allow 10% tolerance


# ============================================================================
# SCALABILITY TESTS
# ============================================================================

class TestScalabilityBenchmarks:
    """Test how MagGeo scales with different data sizes"""
    
    @pytest.mark.parametrize("n_gps_points", [100, 500, 1000, 2000, 5000])
    def test_processing_time_scaling(self, n_gps_points, benchmark):
        """Test how processing time scales with GPS trajectory size"""
        config = MagGeoConfig(token="test", chunk_size=min(100, n_gps_points))
        
        # Generate test data
        gps_data = pd.DataFrame({
            'Latitude': np.random.uniform(50, 60, n_gps_points),
            'Longitude': np.random.uniform(-10, 5, n_gps_points),
            'DateTime': pd.date_range('2023-06-01', periods=n_gps_points, freq='1min'),
            'Altitude': np.random.uniform(0, 10000, n_gps_points)
        })
        
        swarm_data = {
            'A': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
            'B': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}), 
            'C': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]})
        }
        
        processor = MagGeoProcessor(config)
        
        with patch.object(processor.interpolator, 'interpolate_point') as mock_interp:
            mock_interp.return_value = {
                'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': 1000.0,
                'DateTime': dt.datetime.now(), 'N_res': 0, 'E_res': 0, 'C_res': 0,
                'TotalPoints': 1, 'Minimum_Distance': 100, 'Average_Distance': 200
            }
            
            result = benchmark(processor._interpolate_magnetic_fields, gps_data, swarm_data)
            assert len(result) == n_gps_points
    
    @pytest.mark.parametrize("n_swarm_points", [1000, 5000, 10000, 20000])
    def test_swarm_data_size_impact(self, n_swarm_points):
        """Test impact of Swarm data size on processing performance"""
        config = MagGeoConfig(token="test", chunk_size=100)
        gps_data = pd.DataFrame({
            'Latitude': np.random.uniform(50, 60, 500),
            'Longitude': np.random.uniform(-10, 5, 500),
            'DateTime': pd.date_range('2023-06-01', periods=500, freq='1min'),
            'Altitude': np.random.uniform(0, 10000, 500)
        })
        
        # Generate Swarm data of varying sizes
        base_time = dt.datetime(2023, 6, 1, 10, 0, 0)
        swarm_data = {
            'A': pd.DataFrame({
                'timestamp': pd.date_range(base_time, periods=n_swarm_points, freq='10s'),
                'Latitude': np.random.uniform(50, 60, n_swarm_points),
                'Longitude': np.random.uniform(-10, 5, n_swarm_points),
                'B_N_res': np.random.normal(0, 100, n_swarm_points),
                'B_E_res': np.random.normal(0, 100, n_swarm_points),
                'B_C_res': np.random.normal(0, 150, n_swarm_points)
            }),
            'B': pd.DataFrame({'timestamp': [base_time], 'B_N_res': [0]}),
            'C': pd.DataFrame({'timestamp': [base_time], 'B_N_res': [0]})
        }
        
        processor = MagGeoProcessor(config)
        
        with patch.object(processor.interpolator, 'interpolate_point') as mock_interp:
            mock_interp.return_value = {
                'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': 1000.0,
                'DateTime': dt.datetime.now(), 'N_res': 0, 'E_res': 0, 'C_res': 0,
                'TotalPoints': 1, 'Minimum_Distance': 100, 'Average_Distance': 200
            }
            
            start_time = time.time()
            result = processor._interpolate_magnetic_fields(gps_data, swarm_data)
            duration = time.time() - start_time
            
            print(f"Swarm points: {n_swarm_points}, Time: {duration:.3f}s")
            assert len(result) == len(gps_data)


# ============================================================================
# REAL-WORLD SCENARIO BENCHMARKS
# ============================================================================

class TestRealisticScenarios:
    """Benchmark realistic usage scenarios"""
    
    def test_aircraft_flight_scenario(self, benchmark):
        """Simulate processing a typical aircraft flight trajectory"""
        # 4-hour flight, 1-minute GPS sampling
        flight_duration_hours = 4
        sampling_interval_minutes = 1
        n_points = flight_duration_hours * 60 // sampling_interval_minutes
        
        # Realistic flight path (London to Edinburgh)
        start_lat, start_lon = 51.5, -0.1  # London
        end_lat, end_lon = 55.9, -3.2      # Edinburgh
        
        gps_data = pd.DataFrame({
            'Latitude': np.linspace(start_lat, end_lat, n_points) + np.random.normal(0, 0.01, n_points),
            'Longitude': np.linspace(start_lon, end_lon, n_points) + np.random.normal(0, 0.01, n_points),
            'DateTime': pd.date_range('2023-06-01 10:00:00', periods=n_points, freq='1min'),
            'Altitude': np.random.uniform(10000, 12000, n_points)  # Cruise altitude
        })
        
        config = MagGeoConfig(token="test", chunk_size=60)  # 1-hour chunks
        processor = MagGeoProcessor(config)
        
        with patch.object(processor, '_fetch_swarm_data_parallel') as mock_swarm, \
             patch.object(processor.interpolator, 'interpolate_point') as mock_interp, \
             patch.object(processor.chaos_model, 'get_ground_values') as mock_chaos:
            
            # Setup mocks
            mock_swarm.return_value = {
                'A': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
                'B': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
                'C': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]})
            }
            
            mock_interp.return_value = {
                'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': 11000.0,
                'DateTime': dt.datetime.now(), 'N_res': 10.0, 'E_res': 5.0, 'C_res': 15.0,
                'TotalPoints': 8, 'Minimum_Distance': 150.0, 'Average_Distance': 300.0
            }
            
            mock_chaos.return_value = {
                'N': [20000.0] * n_points, 'E': [1000.0] * n_points, 'C': [45000.0] * n_points,
                'N_internal': [19000.0] * n_points, 'E_internal': [900.0] * n_points, 'C_internal': [44000.0] * n_points
            }
            
            result = benchmark(processor.process_trajectory, gps_data)
            assert len(result) == n_points
    
    def test_satellite_orbit_scenario(self):
        """Simulate processing a low-Earth orbit satellite trajectory"""
        # 90-minute orbit, 10-second sampling
        orbit_duration_minutes = 90
        sampling_interval_seconds = 10
        n_points = orbit_duration_minutes * 60 // sampling_interval_seconds
        
        # Simplified circular orbit parameters
        orbit_altitude = 400000  # 400 km altitude
        
        # Generate orbital trajectory
        times = np.linspace(0, 2 * np.pi, n_points)
        orbit_radius = 6371000 + orbit_altitude  # Earth radius + altitude
        
        gps_data = pd.DataFrame({
            'Latitude': np.degrees(np.arcsin(np.sin(np.pi/3) * np.sin(times))),  # Inclined orbit
            'Longitude': np.degrees(times) % 360 - 180,
            'DateTime': pd.date_range('2023-06-01 10:00:00', periods=n_points, freq='10s'),
            'Altitude': np.full(n_points, orbit_altitude)
        })
        
        config = MagGeoConfig(token="test", chunk_size=180)  # 30-minute chunks
        processor = MagGeoProcessor(config)
        
        with patch.object(processor, '_fetch_swarm_data_parallel') as mock_swarm, \
             patch.object(processor.interpolator, 'interpolate_point') as mock_interp, \
             patch.object(processor.chaos_model, 'get_ground_values') as mock_chaos:
            
            # Setup mocks
            mock_swarm.return_value = {
                'A': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
                'B': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
                'C': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]})
            }
            
            mock_interp.return_value = {
                'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': orbit_altitude,
                'DateTime': dt.datetime.now(), 'N_res': 5.0, 'E_res': 3.0, 'C_res': 8.0,
                'TotalPoints': 12, 'Minimum_Distance': 50.0, 'Average_Distance': 100.0
            }
            
            mock_chaos.return_value = {
                'N': [15000.0] * n_points, 'E': [500.0] * n_points, 'C': [35000.0] * n_points,
                'N_internal': [14500.0] * n_points, 'E_internal': [450.0] * n_points, 'C_internal': [34500.0] * n_points
            }
            
            start_time = time.time()
            result = processor.process_trajectory(gps_data)
            duration = time.time() - start_time
            
            print(f"Satellite orbit processing: {n_points} points in {duration:.2f}s")
            print(f"Processing rate: {n_points/duration:.1f} points/second")
            
            assert len(result) == n_points


# ============================================================================
# STRESS TESTS
# ============================================================================

class TestStressScenarios:
    """Stress tests for extreme conditions"""
    
    @pytest.mark.slow
    def test_very_large_dataset(self):
        """Test with very large GPS trajectory (50,000 points)"""
        n_points = 50000
        gps_data = pd.DataFrame({
            'Latitude': np.random.uniform(40, 70, n_points),
            'Longitude': np.random.uniform(-20, 20, n_points),
            'DateTime': pd.date_range('2023-01-01', periods=n_points, freq='1min'),
            'Altitude': np.random.uniform(0, 15000, n_points)
        })
        
        config = MagGeoConfig(token="test", chunk_size=500, max_workers=8)
        processor = MagGeoProcessor(config)
        
        with patch.object(processor, '_fetch_swarm_data_parallel') as mock_swarm, \
             patch.object(processor.interpolator, 'interpolate_point') as mock_interp, \
             patch.object(processor.chaos_model, 'get_ground_values') as mock_chaos:
            
            # Setup mocks for fast processing
            mock_swarm.return_value = {
                'A': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
                'B': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
                'C': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]})
            }
            
            mock_interp.return_value = {
                'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': 1000.0,
                'DateTime': dt.datetime.now(), 'N_res': 0, 'E_res': 0, 'C_res': 0,
                'TotalPoints': 1, 'Minimum_Distance': 100, 'Average_Distance': 200
            }
            
            mock_chaos.return_value = {
                'N': [20000.0] * n_points, 'E': [1000.0] * n_points, 'C': [45000.0] * n_points,
                'N_internal': [19000.0] * n_points, 'E_internal': [900.0] * n_points, 'C_internal': [44000.0] * n_points
            }
            
            start_time = time.time()
            result = processor.process_trajectory(gps_data)
            duration = time.time() - start_time
            
            print(f"Large dataset processing: {n_points} points in {duration:.2f}s")
            print(f"Processing rate: {n_points/duration:.1f} points/second")
            print(f"Memory efficiency: {n_points} points processed successfully")
            
            assert len(result) == n_points
    
    def test_concurrent_processing(self):
        """Test concurrent processing of multiple trajectories"""
        import threading
        
        def process_trajectory(trajectory_id):
            gps_data = pd.DataFrame({
                'Latitude': np.random.uniform(50, 60, 1000),
                'Longitude': np.random.uniform(-10, 5, 1000),
                'DateTime': pd.date_range('2023-06-01', periods=1000, freq='1min'),
                'Altitude': np.random.uniform(0, 10000, 1000)
            })
            
            config = MagGeoConfig(token=f"test_token_{trajectory_id}", chunk_size=100)
            processor = MagGeoProcessor(config)
            
            with patch.object(processor, '_fetch_swarm_data_parallel') as mock_swarm, \
                 patch.object(processor.interpolator, 'interpolate_point') as mock_interp, \
                 patch.object(processor.chaos_model, 'get_ground_values') as mock_chaos:
                
                mock_swarm.return_value = {
                    'A': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
                    'B': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]}),
                    'C': pd.DataFrame({'timestamp': [dt.datetime.now()], 'B_N_res': [0]})
                }
                
                mock_interp.return_value = {
                    'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': 1000.0,
                    'DateTime': dt.datetime.now(), 'N_res': 0, 'E_res': 0, 'C_res': 0,
                    'TotalPoints': 1, 'Minimum_Distance': 100, 'Average_Distance': 200
                }
                
                mock_chaos.return_value = {
                    'N': [20000.0] * 1000, 'E': [1000.0] * 1000, 'C': [45000.0] * 1000,
                    'N_internal': [19000.0] * 1000, 'E_internal': [900.0] * 1000, 'C_internal': [44000.0] * 1000
                }
                
                result = processor.process_trajectory(gps_data)
                return len(result)
        
        # Run multiple processing tasks concurrently
        n_concurrent = 4
        threads = []
        results = []
        
        start_time = time.time()
        
        for i in range(n_concurrent):
            thread = threading.Thread(target=lambda i=i: results.append(process_trajectory(i)))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        duration = time.time() - start_time
        
        print(f"Concurrent processing: {n_concurrent} trajectories in {duration:.2f}s")
        print(f"Results: {results}")
        
        assert len(results) == n_concurrent
        assert all(result == 1000 for result in results)


if __name__ == "__main__":
    # Run benchmarks directly
    pytest.main([__file__, "--benchmark-only", "-v"])'Average_Distance': 200
            }
            
            for chunk_size in chunk_sizes:
                config = MagGeoConfig(token="test", chunk_size=chunk_size)
                processor = MagGeoProcessor(config)
                
                start_time = time.time()
                processor._interpolate_magnetic_fields(gps_data, swarm_data)
                duration = time.time() - start_time
                
                results[chunk_size] = duration
                print(f"Chunk size {chunk_size}: {duration:.3f}s")
        
        # Find optimal chunk size
        optimal_chunk = min(results, key=results.get)
        print(f"Optimal chunk size: {optimal_chunk}")
    
    # ========================================================================
    # MAGNETIC COMPONENT CALCULATION BENCHMARKS
    # ========================================================================
    
    def test_magnetic_components_calculation_vectorized(self, benchmark, benchmark_config):
        """Benchmark vectorized magnetic component calculations"""
        n_points = 10000
        test_data = pd.DataFrame({
            'N': np.random.normal(20000, 1000, n_points),
            'E': np.random.normal(1000, 500, n_points),
            'C': np.random.normal(45000, 2000, n_points)
        })
        
        processor = MagGeoProcessor(benchmark_config)
        
        result = benchmark(processor._calculate_magnetic_components, test_data)
        assert len(result) == n_points
        assert 'H' in result.columns
        assert 'D' in result.columns
        assert 'I' in result.columns
        assert 'F' in result.columns
    
    def test_magnetic_components_vs_loop(self, benchmark_config):
        """Compare vectorized vs loop-based magnetic component calculation"""
        n_points = 5000
        test_data = pd.DataFrame({
            'N': np.random.normal(20000, 1000, n_points),
            'E': np.random.normal(1000, 500, n_points),  
            'C': np.random.normal(45000, 2000, n_points)
        })
        
        processor = MagGeoProcessor(benchmark_config)
        
        # Vectorized approach (current implementation)
        start_time = time.time()
        result_vectorized = processor._calculate_magnetic_components(test_data.copy())
        vectorized_time = time.time() - start_time
        
        # Loop-based approach (for comparison)
        start_time = time.time()
        result_loop = test_data.copy()
        for idx, row in result_loop.iterrows():
            result_loop.loc[idx, 'H'] = np.sqrt(row['N']**2 + row['E']**2)
            result_loop.loc[idx, 'D'] = np.degrees(np.arctan2(row['E'], row['N']))
            result_loop.loc[idx, 'I'] = np.degrees(np.arctan2(row['C'], result_loop.loc[idx, 'H']))
            result_loop.loc[idx, 'F'] = np.sqrt(row['N']**2 + row['E']**2 + row['C']**2)
        loop_time = time.time() - start_time
        
        print(f"Vectorized: {vectorized_time:.3f}s, Loop: {loop_time:.3f}s")
        print(f"Speedup: {loop_time/vectorized_time:.1f}x")
        
        # Verify results are equivalent
        np.testing.assert_array_almost_equal(result_vectorized['H'], result_loop['H'], decimal=2)
    
    # ========================================================================
    # MEMORY USAGE BENCHMARKS
    # ========================================================================
    
    @memory_profiler.profile
    def test_memory_usage_large_dataset(self, benchmark_config):
        """Profile memory usage with large datasets"""
        # This test requires memory_profiler: pip install memory-profiler
        gps_data = self.generate_gps_data(5000)
        swarm_data = self.generate_swarm_data(50000)
        
        with patch('maggeo.core.interpolation.MagneticFieldInterpolator.interpolate_point') as mock_interp:
            mock_interp.return_value = {
                'Latitude': 55.0, 'Longitude': -3.0, 'Altitude': 1000.0,
                'DateTime': dt.datetime.now(), 'N_res': 0, 'E_res': 0, 'C_res': 0,
                'TotalPoints': 1, 'Minimum_Distance': 100,