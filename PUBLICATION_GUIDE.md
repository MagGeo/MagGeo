# MagGeo Publication Guide

Complete instructions for publishing MagGeo v0.2.0 to GitHub and PyPI.

## 1. Git Repository Setup and GitHub Upload

### Step 1.1: Initialize Git Repository (if not already done)

```bash
# Navigate to project directory
cd /Users/fbenitez/Documents/refactor_maggeo

# Initialize git repository
git init

# Set up .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Documentation
docs/_build/
site/

# Data files (keep sample data)
temp_data/
my_swarm_data/
results/
*.parquet
*.h5

# OS
.DS_Store
Thumbs.db

# Jupyter
.ipynb_checkpoints/
EOF
```

### Step 1.2: Add Remote Origin and Configure

```bash
# Add the GitHub repository as remote origin
git remote add origin https://github.com/MagGeo/MagGeo.git

# Set up user credentials (if not already configured)
git config user.name "Fernando Benitez-Paez"
git config user.email "Fernando.Benitez@st-andrews.ac.uk"

# Check remote configuration
git remote -v
```

### Step 1.3: Stage and Commit All Files

```bash
# Add all files (respecting .gitignore)
git add .

# Create initial commit
git commit -m "Refactor MagGeo v0.2.0: Complete package restructure

- Restructured package with proper module organization
- Added SwarmDataManager for unified data handling
- Implemented parallel processing capabilities
- Enhanced CLI interface with comprehensive commands
- Added comprehensive documentation with MkDocs Material
- Improved performance by 5.6x for large trajectories
- Added geomagnetic indices integration (AE/SME)
- Created extensive test suite
- Added Jupyter notebook examples
- Prepared for PyPI publication

Features:
- Core trajectory annotation functions
- Parallel processing for large datasets
- Swarm satellite data management
- Command-line interface
- Comprehensive API documentation
- User guides and examples"
```

### Step 1.4: Create and Push to refactor_maggeo Branch

```bash
# Create and switch to refactor_maggeo branch
git checkout -b refactor_maggeo

# Push to GitHub repository
git push -u origin refactor_maggeo

# Verify the push was successful
git status
```

### Step 1.5: Create Pull Request (Optional for Review)

After pushing, you can create a Pull Request on GitHub:
1. Go to https://github.com/MagGeo/MagGeo
2. Click "Compare & pull request" for the refactor_maggeo branch
3. Add description with improvements summary
4. Request review from collaborators if needed

## 2. Package Validation Checklist

### Step 2.1: Validate Package Structure

```bash
# Check package structure
find . -name "*.py" -path "./maggeo/*" | head -10

# Verify main modules exist
ls -la maggeo/

# Check if __init__.py files are present
find . -name "__init__.py"
```

### Step 2.2: Validate Dependencies

```bash
# Install package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Install documentation dependencies
pip install -e ".[docs]"
```

### Step 2.3: Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=maggeo --cov-report=html

# Check specific core functionality
python -m pytest tests/test_core.py -v
```

### Step 2.4: Validate Package Building

```bash
# Clean any previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build

# Check generated files
ls -la dist/

# Install the built package in a fresh environment
pip install dist/maggeo-0.2.0-py3-none-any.whl
```

### Step 2.5: Test CLI Interface

```bash
# Test CLI commands
maggeo --help
maggeo annotate --help
maggeo swarm --help

# Test basic functionality (if data available)
# maggeo annotate data/sample_data/trajectory_test.csv --output test_output.csv
```

### Step 2.6: Validate Documentation

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material mkdocstrings[python]

# Build documentation
mkdocs build

# Serve documentation locally for testing
mkdocs serve
# Visit http://127.0.0.1:8000 to verify documentation
```

### Step 2.7: Import and Functionality Tests

```python
# Test package imports
python -c "
import maggeo
print(f'MagGeo version: {maggeo.__version__}')

from maggeo.core import annotate_gps_with_geomag
from maggeo.swarm_data_manager import SwarmDataManager
from maggeo.parallel_processing import parallel_maggeo_annotation

print('All main modules imported successfully!')
"
```

## 3. PyPI Publication Steps

### Step 3.1: Pre-publication Checklist

**✅ Required Files Check:**
- [ ] `pyproject.toml` with correct metadata
- [ ] `README.md` with installation and usage instructions
- [ ] `LICENSE` file (MIT License)
- [ ] `MANIFEST.in` for including data files
- [ ] Version number updated to 0.2.0
- [ ] All dependencies specified correctly

**✅ Package Quality Check:**
- [ ] All tests passing
- [ ] Documentation builds without errors
- [ ] Package installs correctly from wheel
- [ ] CLI commands work
- [ ] Import statements work

### Step 3.2: Set Up PyPI Accounts

1. **Create PyPI Account:**
   - Register at https://pypi.org/account/register/
   - Verify email address

2. **Create TestPyPI Account:**
   - Register at https://test.pypi.org/account/register/
   - This is for testing before real publication

3. **Generate API Tokens:**
   - PyPI: Go to https://pypi.org/manage/account/token/
   - TestPyPI: Go to https://test.pypi.org/manage/account/token/
   - Create tokens with appropriate scope

### Step 3.3: Configure Authentication

```bash
# Install twine for uploading
pip install twine

# Create ~/.pypirc file for authentication
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
  username = __token__
  password = YOUR_PYPI_API_TOKEN_HERE

[testpypi]
  username = __token__
  password = YOUR_TESTPYPI_API_TOKEN_HERE

EOF

# Set secure permissions
chmod 600 ~/.pypirc
```

### Step 3.4: Test Publication on TestPyPI

```bash
# Clean build directory
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ maggeo==0.2.0
```

### Step 3.5: Validate TestPyPI Installation

```bash
# Create a fresh virtual environment for testing
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ maggeo==0.2.0

# Test basic functionality
python -c "
import maggeo
print(f'Installed version: {maggeo.__version__}')
print('TestPyPI installation successful!')
"

# Deactivate test environment
deactivate
```

### Step 3.6: Publish to Production PyPI

**⚠️ IMPORTANT: Only proceed if TestPyPI installation worked perfectly!**

```bash
# Clean and rebuild (to ensure fresh package)
rm -rf build/ dist/ *.egg-info/
python -m build

# Upload to production PyPI
twine upload dist/*

# Verify upload
# Visit https://pypi.org/project/maggeo/
```

### Step 3.7: Post-Publication Verification

```bash
# Create fresh environment for final test
python -m venv final_test_env
source final_test_env/bin/activate

# Install from PyPI
pip install maggeo==0.2.0

# Test installation
python -c "
import maggeo
from maggeo.core import annotate_gps_with_geomag
print(f'Successfully installed MagGeo {maggeo.__version__} from PyPI!')
"

# Test CLI
maggeo --version

# Deactivate
deactivate
```

## 4. Final Package Validation Issues Found

### Issue 1: Package Configuration Fix Required

The `pyproject.toml` has an incorrect package structure. Fix this:

```toml
[tool.setuptools]
package-dir = {"" = "."}

[tool.setuptools.packages.find]
where = ["."]
include = ["maggeo*"]
exclude = ["tests*", "docs*", "temp_data*", "my_swarm_data*"]
```

### Issue 2: Repository URLs Need Update

Update repository URLs in `pyproject.toml`:

```toml
[project.urls]
homepage = "https://github.com/MagGeo/MagGeo"
repository = "https://github.com/MagGeo/MagGeo"
documentation = "https://MagGeo.github.io/MagGeo"
```

### Issue 3: CLI Entry Point Validation

Ensure CLI module exists:
```bash
# Check if CLI module exists
ls -la maggeo/cli.py

# If missing, create or fix the entry point
```

## 5. Documentation Deployment (GitHub Pages)

```bash
# Deploy documentation to GitHub Pages
mkdocs gh-deploy --branch gh-pages

# This will:
# 1. Build the documentation
# 2. Push to gh-pages branch
# 3. Enable GitHub Pages at https://MagGeo.github.io/MagGeo
```

## 6. Release Management

### Create GitHub Release

1. Go to https://github.com/MagGeo/MagGeo/releases
2. Click "Create a new release"
3. Tag version: `v0.2.0`
4. Release title: `MagGeo v0.2.0 - Major Refactor`
5. Description: Use content from `improvements_summary.md`
6. Attach built wheel and source distribution

### Version Tagging

```bash
# Tag the release
git tag -a v0.2.0 -m "MagGeo v0.2.0 - Major refactor with performance improvements"

# Push tags
git push origin v0.2.0
```

## 7. Post-Publication Tasks

### Update Documentation Links

1. Update README.md with PyPI installation instructions
2. Update documentation with new package structure
3. Add installation verification examples
4. Update citation information with PyPI reference

### Community Engagement

1. Announce release on relevant scientific forums
2. Update academic profiles with new software version
3. Consider submitting to Journal of Open Source Software (JOSS)
4. Share with movement ecology community

## 8. Maintenance Plan

### Regular Updates
- Monitor PyPI download statistics
- Respond to GitHub issues promptly
- Update dependencies regularly
- Maintain backward compatibility

### Version Management
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Document all changes in CHANGELOG.md
- Test thoroughly before each release

---

## Quick Commands Summary

```bash
# Complete publication workflow
cd /Users/fbenitez/Documents/refactor_maggeo

# 1. Git setup
git init
git remote add origin https://github.com/MagGeo/MagGeo.git
git add .
git commit -m "MagGeo v0.2.0 refactor"
git checkout -b refactor_maggeo
git push -u origin refactor_maggeo

# 2. Validation
pip install -e ".[dev,docs]"
python -m pytest tests/ -v
python -m build
mkdocs build

# 3. PyPI publication
twine upload --repository testpypi dist/*  # Test first
twine upload dist/*  # Production release

# 4. Documentation
mkdocs gh-deploy
```

**🎉 Your MagGeo package is now ready for publication!** 

Follow these steps carefully, and you'll have a professionally published Python package with comprehensive documentation and proper version control.
