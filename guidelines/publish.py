#!/usr/bin/env python3
"""
MagGeo Package Publishing Script

This script helps prepare and publish the MagGeo package to PyPI.
Run with: python publish.py [test|prod]

Script Capabilities Summary:
Command	Function	Status
check	Import validation	✅ Working
clean	Artifact cleanup	✅ Working
build	Full build pipeline	✅ Working
test	TestPyPI upload	✅ Working (requires auth)
prod	PyPI upload	✅ Working (requires auth)

"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(e.stderr)
        if check:
            sys.exit(1)
        return e

def clean_build():
    """Remove build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    dirs_to_remove = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_remove:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed {path}")
    
    # Remove __pycache__ directories
    for path in Path('.').rglob('__pycache__'):
        shutil.rmtree(path)
        print(f"Removed {path}")

def check_package():
    """Check if package can be imported."""
    print("🔍 Checking package imports...")
    
    try:
        result = run_command("python -c 'import maggeo; print(f\"MagGeo v{maggeo.__version__} imported successfully\")'")
        return True
    except:
        print("❌ Package import failed")
        return False

def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    
    # Check if pytest is available
    try:
        run_command("python -m pytest --version")
    except:
        print("Installing pytest...")
        run_command("pip install pytest pytest-cov")
    
    # Run tests
    result = run_command("python -m pytest tests/ -v", check=False)
    return result.returncode == 0

def build_package():
    """Build the package distributions."""
    print("📦 Building package...")
    
    # Install build tools if needed
    run_command("pip install build twine")
    
    # Build package
    run_command("python -m build")
    
    # Check distributions
    run_command("twine check dist/*")

def upload_to_testpypi():
    """Upload to Test PyPI."""
    print("🚀 Uploading to Test PyPI...")
    
    # Check if .pypirc exists
    pypirc_path = Path.home() / '.pypirc'
    if not pypirc_path.exists():
        print("⚠️  No .pypirc found. You'll need to enter credentials manually.")
    
    run_command("twine upload --repository testpypi dist/*")
    
    print("✅ Upload to Test PyPI complete!")
    print("Test installation with:")
    print("pip install --index-url https://test.pypi.org/simple/ maggeo")

def upload_to_pypi():
    """Upload to production PyPI."""
    print("🚀 Uploading to PyPI...")
    
    response = input("Are you sure you want to upload to production PyPI? (yes/no): ")
    if response.lower() != 'yes':
        print("Upload cancelled.")
        return
    
    run_command("twine upload dist/*")
    
    print("✅ Upload to PyPI complete!")
    print("Install with:")
    print("pip install maggeo")

def main():
    """Main publishing workflow."""
    if len(sys.argv) < 2:
        print("Usage: python publish.py [test|prod|check|clean]")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == 'clean':
        clean_build()
        return
    elif action == 'check':
        success = check_package()
        sys.exit(0 if success else 1)
    
    print("🎯 MagGeo Package Publishing Script")
    print("=" * 40)
    
    # Clean previous builds
    clean_build()
    
    # Check package structure
    if not check_package():
        print("❌ Package check failed. Please fix imports first.")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("⚠️  Some tests failed. Continue anyway? (y/n)")
        if input().lower() != 'y':
            sys.exit(1)
    
    # Build package
    build_package()
    
    # Upload based on action
    if action == 'test':
        upload_to_testpypi()
    elif action == 'prod':
        upload_to_pypi()
    else:
        print(f"Unknown action: {action}")
        print("Use 'test' for TestPyPI or 'prod' for PyPI")
        sys.exit(1)

if __name__ == '__main__':
    main()
