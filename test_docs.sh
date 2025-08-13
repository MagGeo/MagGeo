#!/bin/bash

# Test documentation script for MagGeo
# This script helps test the MkDocs documentation site locally

echo "🔧 Setting up documentation environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "docs_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv docs_env
fi

# Activate environment
echo "🔄 Activating virtual environment..."
source docs_env/bin/activate

# Function to install dependencies
install_deps() {
    echo "📚 Installing documentation dependencies..."
    pip install --upgrade pip
    pip install -e ".[docs]"
}

# Function to build MkDocs docs
build_docs() {
    echo "🏗️  Building MkDocs documentation..."
    mkdocs build
    if [ $? -eq 0 ]; then
        echo "✅ Documentation built successfully!"
        echo "📁 Built files are in: ./site/"
    else
        echo "❌ Documentation build failed!"
        return 1
    fi
}

# Function to serve MkDocs docs locally
serve_docs() {
    echo "🚀 Starting local MkDocs documentation server..."
    echo "📖 Documentation will be available at: http://127.0.0.1:8000/"
    echo "🛑 Press Ctrl+C to stop the server"
    mkdocs serve
}

# Function to build docs (strict mode)
build_docs_strict() {
    echo "🏗️  Building documentation (strict mode)..."
    mkdocs build --strict
    if [ $? -eq 0 ]; then
        echo "✅ Documentation built successfully!"
        echo "📁 Built files are in: ./site/"
    else
        echo "❌ Documentation build failed!"
        return 1
    fi
}

# Function to clean build
clean_docs() {
    echo "🧹 Cleaning documentation builds..."
    rm -rf site/
    echo "✅ Clean complete!"
}

# Function to validate documentation
validate_docs() {
    echo "🔍 Validating documentation..."
    install_deps
    
    echo ""
    echo "=== Building MkDocs Documentation ==="
    build_docs_strict
    result=$?
    
    if [ $result -eq 0 ]; then
        echo ""
        echo "🎉 Documentation built successfully!"
        echo "📁 Docs: ./site/"
        return 0
    else
        echo ""
        echo "❌ Documentation build failed!"
        return 1
    fi
}

# Parse command line arguments
case "${1:-help}" in
    "install")
        install_deps
        ;;
    "build")
        install_deps
        build_docs
        ;;
    "build-strict")
        install_deps
        build_docs_strict
        ;;
    "serve")
        install_deps
        serve_docs
        ;;
    "clean")
        clean_docs
        ;;
    "validate")
        validate_docs
        ;;
    "help")
        echo "📋 Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  install      - Install documentation dependencies"
        echo "  build        - Build MkDocs documentation"
        echo "  build-strict - Build docs with strict mode (fails on warnings)"
        echo "  serve        - Build and serve docs locally at :8000"
        echo "  clean        - Clean build directory"
        echo "  validate     - Validate documentation build"
        echo "  help         - Show this help"
        echo ""
        echo "🌐 Site will be available at:"
        echo "   Documentation: http://127.0.0.1:8000/"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "🆘 Use '$0 help' for usage information"
        exit 1
        ;;
esac
