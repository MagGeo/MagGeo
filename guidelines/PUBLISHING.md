# MagGeo Publishing Checklist

## Pre-Release Checklist

### ✅ Code Quality
- [ ] All imports work correctly
- [ ] Tests pass in multiple Python versions (3.8, 3.9, 3.10, 3.11)
- [ ] Documentation is up to date
- [ ] Version numbers match across all files
- [ ] Dependencies are properly specified

### ✅ Package Structure
- [ ] `setup.py` is correctly configured
- [ ] `pyproject.toml` matches setup.py
- [ ] `__init__.py` exposes main functions
- [ ] `MANIFEST.in` includes necessary files
- [ ] `.gitignore` excludes build artifacts

### ✅ Documentation
- [ ] README.md is comprehensive
- [ ] CHANGELOG.md is updated
- [ ] CONTRIBUTING.md exists
- [ ] License is included
- [ ] Examples/notebooks work

### ✅ Testing
- [ ] Unit tests cover main functionality
- [ ] Integration tests pass
- [ ] Package can be installed and imported
- [ ] Command-line interface works (if applicable)

## Release Process

### 1. Version Management
```bash
# Update version in:
# - setup.py
# - pyproject.toml
# - maggeo/__init__.py
# - CHANGELOG.md
```

### 2. Testing
```bash
# Test in clean environment
conda create -n maggeo-release-test python=3.9
conda activate maggeo-release-test
pip install -e .
python -c "import maggeo; print('Success!')"
```

### 3. Build and Test Upload
```bash
# Clean and build
python publish.py clean
python publish.py test
```

### 4. Production Release
```bash
# After testing on TestPyPI
python publish.py prod
```

### 5. Post-Release
- [ ] Create GitHub release with tag
- [ ] Update documentation website
- [ ] Announce on relevant channels
- [ ] Monitor for issues

## Troubleshooting Common Issues

### Import Errors
- Check all relative imports use `.` notation
- Ensure dependencies are correctly specified
- Test in fresh environment

### Build Failures
- Remove all `__pycache__` directories
- Check MANIFEST.in includes all necessary files
- Verify setup.py configuration

### Upload Issues
- Configure `.pypirc` with API tokens
- Ensure unique version number
- Check package name availability

## Quick Commands

```bash
# Check package status
python publish.py check

# Clean build artifacts
python publish.py clean

# Upload to TestPyPI
python publish.py test

# Upload to PyPI (production)
python publish.py prod
```
