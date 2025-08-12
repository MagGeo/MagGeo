#!/bin/bash

# Test documentation script for MagGeo
# This script helps test the MkDocs site locally

echo "🔧 Setting up documentation environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "docs_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv docs_env
fi

# Activate environment
echo "🔄 Activating virtual environment..."
source docs_env/bin/activate

# Install dependencies
echo "📚 Installing documentation dependencies..."
pip install -e ".[docs]"

# Function to build docs
build_docs() {
    echo "🏗️  Building documentation..."
    mkdocs build
    if [ $? -eq 0 ]; then
        echo "✅ Documentation built successfully!"
        echo "📁 Built files are in: ./site/"
    else
        echo "❌ Documentation build failed!"
        exit 1
    fi
}

# Function to serve docs locally
serve_docs() {
    echo "🚀 Starting local documentation server..."
    echo "📖 Documentation will be available at: http://127.0.0.1:8001/"
    echo "🛑 Press Ctrl+C to stop the server"
    mkdocs serve --dev-addr 127.0.0.1:8001
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
        exit 1
    fi
}

# Function to clean build
clean_docs() {
    echo "🧹 Cleaning documentation build..."
    rm -rf site/
    echo "✅ Clean complete!"
}

# Parse command line arguments
case "${1:-serve}" in
    "build")
        build_docs
        ;;
    "build-strict")
        build_docs_strict
        ;;
    "serve")
        build_docs
        serve_docs
        ;;
    "clean")
        clean_docs
        ;;
    "help")
        echo "📋 Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  serve        - Build and serve docs locally (default)"
        echo "  build        - Build docs only"
        echo "  build-strict - Build docs with strict mode (fails on warnings)"
        echo "  clean        - Clean build directory" 
        echo "  help         - Show this help"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "🆘 Use '$0 help' for usage information"
        exit 1
        ;;
esac
