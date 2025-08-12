#!/bin/bash
# MagGeo Update Testing Script
# Tests a new version from TestPyPI before production deployment

set -e  # Exit on any error

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "❌ Error: Version number required"
    echo "Usage: ./test_update.sh <version>"
    echo "Example: ./test_update.sh 0.2.2"
    exit 1
fi

echo "🧪 Testing MagGeo v$VERSION update from TestPyPI..."
echo "=================================================="

# Create isolated test environment
echo "🔧 Creating test environment..."
python3 -m venv test_env_$VERSION
source test_env_$VERSION/bin/activate

# Install from TestPyPI
echo "📦 Installing maggeo v$VERSION from TestPyPI..."
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ maggeo==$VERSION

# Run comprehensive tests
echo "🔍 Running functionality tests..."
python -c "
import sys
import maggeo

# Version check
print(f'📋 Installed version: {maggeo.__version__}')
assert maggeo.__version__ == '$VERSION', f'❌ Version mismatch: {maggeo.__version__} != $VERSION'
print('✅ Version check passed')

# Import tests
try:
    from maggeo.core import annotate_gps_with_geomag
    from maggeo.swarm_data_manager import SwarmDataManager
    from maggeo.parallel_processing import parallel_maggeo_annotation
    print('✅ Core modules import successful')
    
    # Test optional modules
    try:
        from maggeo import indices, gps, interpolation
        print('✅ All optional modules import successful')
    except ImportError as e:
        print(f'⚠️  Some optional modules failed: {e}')
        print('✅ Core functionality available')
        
except ImportError as e:
    print(f'❌ Critical import error: {e}')
    sys.exit(1)

# Basic functionality test
try:
    # Test SwarmDataManager instantiation
    sdm = SwarmDataManager()
    print('✅ SwarmDataManager instantiation successful')
except Exception as e:
    print(f'❌ SwarmDataManager error: {e}')
    sys.exit(1)

print('✅ All functionality tests passed')
"

# Test CLI interface
echo "🖥️  Testing CLI interface..."
echo "CLI Version: $(maggeo --version)"
maggeo --help > /dev/null
maggeo annotate --help > /dev/null
maggeo swarm --help > /dev/null
echo "✅ CLI tests passed"

# Cleanup
echo "🧹 Cleaning up test environment..."
deactivate
rm -rf test_env_$VERSION

echo ""
echo "🎉 SUCCESS: MagGeo v$VERSION passed all tests!"
echo "✅ Ready for production PyPI deployment"
echo ""
echo "Next steps:"
echo "1. Review test results above"
echo "2. If all tests passed, deploy to production:"
echo "   twine upload dist/*"
echo "3. Verify production deployment with:"
echo "   pip install maggeo==$VERSION"
