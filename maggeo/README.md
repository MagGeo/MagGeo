# MagGeo Refactoring Plan & Testing Strategy
This is the folder where I am including the new and refactored version of MagGeo, including the plan, package structure and other changes I would like to implement.

## URGENT Changes Required

### 1. **Code Structure & Architecture**

-   **Split monolithic main() function** (200+ lines) into smaller, focused functions
-   **Remove hardcoded paths** - make everything configurable
-   **Separate CLI from core logic** - create a proper API that can be imported
-   **Add proper error handling** with specific exception types
-   **Remove bare except blocks** that hide errors

### 2. **Performance Critical Issues**

-   **Eliminate redundant file I/O**: Currently writing/reading CSV files unnecessarily
-   **Optimize pandas operations**: Remove intermediate CSV saves in temp directory
-   **Vectorize calculations** instead of iterating through DataFrames
-   **Memory management**: Process data in chunks for large GPS trajectories
-   **Parallel processing**: Use multiprocessing for independent Swarm data fetching

### 3. **Data Handling & Validation**

-   **Input validation**: Check GPS data format, coordinate ranges, date formats
-   **Type hints**: Add throughout for better IDE support and documentation
-   **Configuration schema validation**: Use pydantic or similar for parameter validation
-   **Handle missing/invalid data**: Graceful degradation instead of crashes

## 📁 Suggested Package Structure

```         
maggeo/
├── maggeo/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── processor.py      # Main MagGeo class
│   │   ├── swarm_client.py   # Swarm data fetching
│   │   ├── interpolation.py  # ST_IDW_Process logic
│   │   └── chaos_model.py    # CHAOS ground values
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── gps_utils.py      # GPS data handling
│   │   ├── validation.py     # Input validation
│   │   └── config.py         # Configuration management
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py           # Click CLI interface
│   └── exceptions.py         # Custom exceptions
├── tests/
├── docs/
├── examples/
├── pyproject.toml
└── README.md
```

## 🔧 Refactored Core Architecture

### Main Processor Class

``` python
class MagGeoProcessor:
    def __init__(self, config: MagGeoConfig):
        self.config = config
        self.swarm_client = SwarmClient(config.token)
    
    def process_trajectory(self, gps_data: pd.DataFrame) -> pd.DataFrame:
        """Main processing pipeline"""
        pass
    
    def _fetch_swarm_data(self, dates: List[date]) -> Dict[str, pd.DataFrame]:
        """Parallel Swarm data fetching"""
        pass
    
    def _interpolate_magnetic_field(self, gps_point, swarm_data) -> Dict:
        """Vectorized interpolation"""
        pass
```

## 🧪 Testing Strategy

### 1. Unit Tests (`tests/unit/`)

-   Test each module independently
-   Mock external API calls (Swarm VirES)
-   Test edge cases and error conditions
-   Validate mathematical calculations

### 2. Integration Tests (`tests/integration/`)

-   Test full pipeline with sample data
-   Test CLI interface
-   Test configuration loading
-   Test file I/O operations

### 3. Performance Tests (`tests/performance/`)

-   Benchmark processing speed
-   Memory usage profiling
-   Large dataset handling

### 4. Documentation Tests (`tests/docs/`)

-   Validate Quarto documentation builds
-   Check example notebooks run correctly
-   Test API documentation completeness

## 📋 Required Testing Scripts

### GitHub Actions Workflow (`.github/workflows/ci.yml`)

``` yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e .[dev]
    
    - name: Run tests
      run: |
        pytest tests/ --cov=maggeo --cov-report=xml
    
    - name: Performance tests
      run: |
        python tests/performance/benchmark.py
    
    - name: Documentation tests
      run: |
        python tests/docs/test_quarto_build.py
```

### Test Scripts to Create

#### 1. `tests/test_core_functionality.py`

``` python
import pytest
import pandas as pd
import numpy as np
from maggeo.core.processor import MagGeoProcessor
from maggeo.utils.config import MagGeoConfig

class TestMagGeoProcessor:
    def test_gps_data_loading(self):
        # Test GPS data validation and loading
        pass
    
    def test_swarm_data_fetching(self):
        # Test Swarm API integration with mocked responses
        pass
    
    def test_magnetic_field_interpolation(self):
        # Test ST_IDW interpolation algorithm
        pass
    
    def test_chaos_model_integration(self):
        # Test CHAOS ground values calculation
        pass
```

#### 2. `tests/test_cli.py`

``` python
from click.testing import CliRunner
from maggeo.cli.main import main

def test_cli_basic_functionality():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create test files and run CLI
        result = runner.invoke(main, ['--parameters-file', 'test_params.yaml'])
        assert result.exit_code == 0
```

#### 3. `tests/performance/benchmark.py`

``` python
import time
import pandas as pd
from maggeo.core.processor import MagGeoProcessor

def benchmark_processing_speed():
    # Test with various GPS trajectory sizes
    sizes = [100, 1000, 10000]
    for size in sizes:
        gps_data = generate_test_gps_data(size)
        start_time = time.time()
        processor.process_trajectory(gps_data)
        duration = time.time() - start_time
        print(f"Size {size}: {duration:.2f}s")
```

#### 4. `tests/docs/test_quarto_build.py`

``` python
import subprocess
import os
from pathlib import Path

def test_quarto_documentation_build():
    """Test that Quarto documentation builds successfully"""
    docs_dir = Path("docs")
    
    # Test Quarto build
    result = subprocess.run(
        ["quarto", "render", str(docs_dir)],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Quarto build failed: {result.stderr}"
    
    # Check that HTML files were generated
    output_dir = docs_dir / "_site"
    assert output_dir.exists(), "Documentation output directory not created"
    
    html_files = list(output_dir.glob("**/*.html"))
    assert len(html_files) > 0, "No HTML files generated"

def test_example_notebooks():
    """Test that example Jupyter notebooks run without errors"""
    notebooks = Path("examples").glob("*.ipynb")
    
    for notebook in notebooks:
        result = subprocess.run(
            ["jupyter", "nbconvert", "--execute", "--to", "notebook", str(notebook)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Notebook {notebook} failed: {result.stderr}"
```

#### 5. `tests/conftest.py` (Pytest Configuration)

``` python
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

@pytest.fixture
def sample_gps_data():
    """Generate sample GPS trajectory data for testing"""
    return pd.DataFrame({
        'Latitude': np.random.uniform(-90, 90, 100),
        'Longitude': np.random.uniform(-180, 180, 100),
        'DateTime': pd.date_range('2023-01-01', periods=100, freq='1H'),
        'Altitude': np.random.uniform(0, 1000, 100)
    })

@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'maggeo': {
            'gpsfilename': 'test_gps.csv',
            'Lat': 'Latitude',
            'Long': 'Longitude',
            'DateTime': 'DateTime',
            'altitude': 'Altitude'
        }
    }
```

## 📦 Package Configuration

### `pyproject.toml`

``` toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "maggeo"
version = "1.0.0"
description = "Geomagnetic field interpolation for GPS trajectories using Swarm satellite data"
authors = [{name = "Fernando Benitez-Paez", email = "your.email@example.com"}]
dependencies = [
    "pandas>=1.5.0",
    "numpy>=1.20.0",
    "viresclient>=0.11.0",
    "pyyaml>=6.0",
    "click>=8.0.0",
    "tqdm>=4.64.0",
    "matplotlib>=3.5.0",
    "scipy>=1.9.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=0.991",
    "jupyter>=1.0.0"
]

[project.scripts]
maggeo = "maggeo.cli.main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--strict-markers --disable-warnings"
```

## 🔍 Code Quality Tools

### Pre-commit Configuration (`.pre-commit-config.yaml`)

``` yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
      - id: mypy
```

## 🚀 Implementation Priority

1.  **Week 1**: Restructure code architecture, separate concerns
2.  **Week 2**: Implement proper error handling and validation
3.  **Week 3**: Optimize performance bottlenecks
4.  **Week 4**: Create comprehensive test suite
5.  **Week 5**: Set up CI/CD pipeline and documentation tests
6.  **Week 6**: Package for PyPI distribution

This refactoring will transform your script into a professional, maintainable library ready for distribution and collaborative development.