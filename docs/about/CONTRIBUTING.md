# Contributing to MagGeo

We welcome contributions to MagGeo! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MagGeo/MagGeo-Annotation-Program.git
   cd MagGeo-Annotation-Program
   ```

2. **Create a virtual environment:**
   ```bash
   conda env create -f environment.yml
   conda activate MagGeoEnv
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=maggeo --cov-report=html
```

## Code Style

We use Black for code formatting and flake8 for linting:

```bash
# Format code
black maggeo/ tests/

# Check linting
flake8 maggeo/ tests/
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Reporting Issues

Please use the GitHub issue tracker to report bugs or request features. Include:
- Python version
- Operating system
- Steps to reproduce the issue
- Expected behavior
- Actual behavior

## Documentation

Documentation improvements are always welcome! We use:
- Docstrings for function documentation
- README.md for general usage
- Jupyter notebooks for examples

Thank you for contributing to MagGeo!
