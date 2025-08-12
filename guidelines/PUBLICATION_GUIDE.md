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

## 8. Future Updates Workflow

### Overview: Safe Update Process
For all future updates, follow this two-stage process:
1. **Stage 1:** Test on TestPyPI with incremented version
2. **Stage 2:** Deploy to Production PyPI only after TestPyPI validation

### Step 8.1: Pre-Update Preparation

**Version Number Strategy:**
- **Patch updates** (bug fixes): 0.2.1 → 0.2.2
- **Minor updates** (new features): 0.2.1 → 0.3.0  
- **Major updates** (breaking changes): 0.2.1 → 1.0.0

**Required Checklist Before Any Update:**
```bash
# 1. Ensure all changes are committed
cd /Users/fbenitez/Documents/refactor_maggeo
git status  # Should show "working tree clean"

# 2. Run full test suite
python -m pytest tests/ -v --cov=maggeo

# 3. Validate package structure
python -c "
import maggeo
from maggeo.core import annotate_gps_with_geomag
from maggeo.swarm_data_manager import SwarmDataManager
print('✅ All imports working')
"

# 4. Test CLI functionality
maggeo --help
maggeo --version
```

### Step 8.2: Update Version Numbers

**Update both files with new version:**

```bash
# Example: Updating from 0.2.1 to 0.2.2
# File 1: pyproject.toml
sed -i '' 's/version = "0.2.1"/version = "0.2.2"/' pyproject.toml

# File 2: maggeo/__init__.py  
sed -i '' 's/__version__ = "0.2.1"/__version__ = "0.2.2"/' maggeo/__init__.py

# Verify changes
grep 'version = ' pyproject.toml
grep '__version__ = ' maggeo/__init__.py
```

**Or manually update:**
- `pyproject.toml`: Line ~7: `version = "0.2.2"`
- `maggeo/__init__.py`: Line ~16: `__version__ = "0.2.2"`

### Step 8.3: Repository Update Process

```bash
# 1. Stage all changes
git add .

# 2. Commit with descriptive message
git commit -m "Update to v0.2.2: [Brief description of changes]

- [List specific changes]
- [Bug fixes or new features]
- [Any breaking changes]"

# 3. Push to GitHub
git push origin refactor_maggeo

# 4. Verify GitHub push successful
git status
```

### Step 8.4: Build Updated Package

```bash
# 1. Clean previous builds
rm -rf build/ dist/ *.egg-info/

# 2. Build new package
python -m build

# 3. Verify build files
ls -la dist/
# Should show: maggeo-0.2.2-py3-none-any.whl and maggeo-0.2.2.tar.gz

# 4. Quick package validation
python -m tarfile -l dist/maggeo-0.2.2.tar.gz | head -10
```

### Step 8.5: STAGE 1 - TestPyPI Deployment & Testing

**Upload to TestPyPI:**
```bash
# Upload to TestPyPI for testing
twine upload --repository testpypi dist/*

# Verify upload success
echo "✅ Package uploaded to: https://test.pypi.org/project/maggeo/0.2.2/"
```

**Comprehensive TestPyPI Validation:**
```bash
# 1. Create isolated test environment
python3 -m venv test_pypi_env
source test_pypi_env/bin/activate

# 2. Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ maggeo==0.2.2

# 3. Test Core Functionality
python -c "
import maggeo
print(f'✅ Version: {maggeo.__version__}')

# Test main imports
from maggeo.core import annotate_gps_with_geomag
from maggeo.swarm_data_manager import SwarmDataManager
from maggeo.parallel_processing import parallel_maggeo_annotation
from maggeo import indices, gps, interpolation
print('✅ All modules import successfully')

# Test basic functionality (if you have test data)
# Add specific tests for your changes here
print('✅ Basic functionality verified')
"

# 4. Test CLI Interface
maggeo --version
maggeo --help
maggeo annotate --help
maggeo swarm --help

# 5. Test with Sample Data (if available)
# maggeo annotate data/sample_data/trajectory_test.csv --output test_update.csv

echo "✅ TestPyPI testing complete"

# 6. Clean up test environment
deactivate
rm -rf test_pypi_env
```

**TestPyPI Validation Checklist:**
- [ ] Package installs without errors
- [ ] All modules import correctly
- [ ] CLI commands work properly
- [ ] Version number is correct
- [ ] New features/fixes work as expected
- [ ] No regression in existing functionality

### Step 8.6: STAGE 2 - Production PyPI Deployment

**⚠️ CRITICAL: Only proceed if ALL TestPyPI tests pass!**

```bash
# 1. Final verification before production
echo "🔍 Pre-production checklist:"
echo "✅ TestPyPI installation successful?"
echo "✅ All functionality tests passed?"
echo "✅ Version numbers correct?"
echo "✅ No breaking changes without major version bump?"
read -p "Continue to production PyPI? (y/N): " confirm

if [[ $confirm == [yY] ]]; then
    # 2. Upload to Production PyPI
    twine upload dist/*
    
    echo "🎉 Successfully uploaded to PyPI!"
    echo "📦 Package available at: https://pypi.org/project/maggeo/0.2.2/"
else
    echo "❌ Production upload cancelled"
fi
```

### Step 8.7: Post-Deployment Verification

**Verify Production Installation:**
```bash
# 1. Create fresh environment for production test
python3 -m venv prod_test_env
source prod_test_env/bin/activate

# 2. Install from production PyPI
pip install maggeo==0.2.2

# 3. Final verification
python -c "
import maggeo
print(f'🎉 Production PyPI - MagGeo {maggeo.__version__} installed successfully!')

# Quick functionality test
from maggeo.core import annotate_gps_with_geomag
print('✅ Production package working correctly')
"

# 4. Test CLI
maggeo --version

# 5. Clean up
deactivate
rm -rf prod_test_env

echo "✅ Production deployment verified!"
```

### Step 8.8: Update Documentation & Releases

```bash
# 1. Update documentation (if needed)
mkdocs build
mkdocs serve  # Test locally at http://127.0.0.1:8001

# 2. Deploy documentation updates
mkdocs gh-deploy

# 3. Create GitHub release
git tag -a v0.2.2 -m "MagGeo v0.2.2 - [Brief description]"
git push origin v0.2.2

# 4. Create GitHub Release via web interface:
# - Go to: https://github.com/MagGeo/MagGeo/releases
# - Click "Create a new release"
# - Tag: v0.2.2
# - Title: "MagGeo v0.2.2 - [Description]"
# - Description: Detail the changes
# - Attach: dist/maggeo-0.2.2.tar.gz and dist/maggeo-0.2.2-py3-none-any.whl
```

### Step 8.9: Common Update Scenarios

**Scenario 1: Bug Fix (Patch Update)**
```bash
# Example: 0.2.1 → 0.2.2
# 1. Fix the bug in code
# 2. Update version numbers
# 3. Follow full workflow above
# 4. Test thoroughly in TestPyPI
# 5. Deploy to production
```

**Scenario 2: New Feature (Minor Update)**
```bash
# Example: 0.2.1 → 0.3.0
# 1. Implement new feature
# 2. Add tests for new functionality
# 3. Update documentation
# 4. Update version to 0.3.0
# 5. Follow full workflow
# 6. Emphasize new features in release notes
```

**Scenario 3: Breaking Changes (Major Update)**
```bash
# Example: 0.2.1 → 1.0.0
# 1. Implement breaking changes
# 2. Update all affected documentation
# 3. Add migration guide
# 4. Update version to 1.0.0
# 5. Follow full workflow
# 6. Clearly document breaking changes
```

### Step 8.10: Rollback Procedure (Emergency)

**If issues are discovered after production deployment:**

```bash
# 1. Identify the last working version
LAST_GOOD_VERSION="0.2.1"

# 2. Quick hotfix approach:
# Option A: Create hotfix branch
git checkout -b hotfix-v0.2.3
# Fix the critical issue
# Update version to 0.2.3
# Follow rapid deployment

# Option B: Advise users to downgrade
echo "Advise users: pip install maggeo==$LAST_GOOD_VERSION"

# 3. Remove problematic version (if critical)
# Note: PyPI doesn't allow deletion, but you can mark as yanked
# This requires manual intervention via PyPI web interface
```

### Step 8.11: Automated Testing Script

**Create update testing script (`test_update.sh`):**
```bash
#!/bin/bash
# Save this as test_update.sh and make executable: chmod +x test_update.sh

set -e  # Exit on any error

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./test_update.sh <version>"
    echo "Example: ./test_update.sh 0.2.2"
    exit 1
fi

echo "🧪 Testing MagGeo v$VERSION update..."

# Create test environment
python3 -m venv test_env_$VERSION
source test_env_$VERSION/bin/activate

# Install from TestPyPI
echo "📦 Installing from TestPyPI..."
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ maggeo==$VERSION

# Run tests
echo "🔍 Running functionality tests..."
python -c "
import maggeo
assert maggeo.__version__ == '$VERSION', f'Version mismatch: {maggeo.__version__} != $VERSION'
from maggeo.core import annotate_gps_with_geomag
from maggeo.swarm_data_manager import SwarmDataManager
print('✅ All tests passed')
"

# Test CLI
maggeo --version

# Cleanup
deactivate
rm -rf test_env_$VERSION

echo "✅ Update test completed successfully for v$VERSION"
```

## 9. Maintenance Plan

### Regular Updates
- Monitor PyPI download statistics
- Respond to GitHub issues promptly
- Update dependencies regularly
- Maintain backward compatibility

### Version Management
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Document all changes in CHANGELOG.md
- Test thoroughly before each release

### Quality Assurance
- Always test on TestPyPI first
- Never skip the validation steps
- Maintain comprehensive test coverage
- Document all breaking changes

---

## Quick Commands Summary

### Initial Publication Workflow
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

### Future Updates Quick Workflow
```bash
# Complete update workflow (example: 0.2.1 → 0.2.2)
cd /Users/fbenitez/Documents/refactor_maggeo

# 1. Update version numbers
sed -i '' 's/version = "0.2.1"/version = "0.2.2"/' pyproject.toml
sed -i '' 's/__version__ = "0.2.1"/__version__ = "0.2.2"/' maggeo/__init__.py

# 2. Commit and push
git add .
git commit -m "Update to v0.2.2: [description of changes]"
git push origin refactor_maggeo

# 3. Build and test on TestPyPI
rm -rf build/ dist/ *.egg-info/
python -m build
twine upload --repository testpypi dist/*

# 4. Automated testing
./test_update.sh 0.2.2

# 5. Production deployment (only if tests pass)
twine upload dist/*

# 6. Create release
git tag -a v0.2.2 -m "MagGeo v0.2.2"
git push origin v0.2.2
```

### Emergency Hotfix Workflow
```bash
# For critical bug fixes
cd /Users/fbenitez/Documents/refactor_maggeo

# 1. Create hotfix branch
git checkout -b hotfix-v0.2.3

# 2. Fix the issue and update version
# ... make fixes ...
sed -i '' 's/version = "0.2.2"/version = "0.2.3"/' pyproject.toml
sed -i '' 's/__version__ = "0.2.2"/__version__ = "0.2.3"/' maggeo/__init__.py

# 3. Rapid deployment
git add .
git commit -m "Hotfix v0.2.3: Critical bug fix"
git push origin hotfix-v0.2.3
python -m build
twine upload --repository testpypi dist/*
./test_update.sh 0.2.3  # Quick validation
twine upload dist/*  # If tests pass
```

**🎉 Your MagGeo package is now ready for publication!** 

Follow these steps carefully, and you'll have a professionally published Python package with comprehensive documentation and proper version control.
