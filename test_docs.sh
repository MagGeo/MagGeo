#!/bin/bash

# Test documentation script for MagGeo
# This script helps test both MkDocs API site and Quarto main site locally

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
    
    # Install Quarto if not available
    if ! command -v quarto &> /dev/null; then
        echo "📦 Quarto not found. Please install Quarto from https://quarto.org/docs/get-started/"
        echo "💡 On macOS: brew install quarto"
        echo "💡 On Ubuntu: See https://quarto.org/docs/get-started/"
        exit 1
    fi
}

# Function to build MkDocs API docs
build_api_docs() {
    echo "🏗️  Building MkDocs API documentation..."
    mkdocs build
    if [ $? -eq 0 ]; then
        echo "✅ API documentation built successfully!"
        echo "📁 Built files are in: ./site/"
    else
        echo "❌ API documentation build failed!"
        return 1
    fi
}

# Function to build Quarto docs
build_quarto_docs() {
    echo "🏗️  Building Quarto documentation..."
    cd docs
    quarto render
    if [ $? -eq 0 ]; then
        echo "✅ Quarto documentation built successfully!"
        echo "📁 Built files are in: ./docs/_book/"
        cd ..
    else
        echo "❌ Quarto documentation build failed!"
        cd ..
        return 1
    fi
}

# Function to serve MkDocs API docs locally
serve_api_docs() {
    echo "🚀 Starting local MkDocs API documentation server..."
    echo "📖 API Documentation will be available at: http://127.0.0.1:8001/"
    echo "🛑 Press Ctrl+C to stop the server"
    mkdocs serve --dev-addr 127.0.0.1:8001
}

# Function to serve Quarto docs locally
serve_quarto_docs() {
    echo "🚀 Starting local Quarto documentation server..."
    echo "📖 Quarto Documentation will be available at: http://127.0.0.1:8002/"
    echo "🛑 Press Ctrl+C to stop the server"
    cd docs
    quarto preview --port 8002
    cd ..
}

# Function to serve both docs (requires two terminals)
serve_both_docs() {
    echo "🚀 To serve both documentation sites simultaneously:"
    echo "📖 Terminal 1: Run './test_docs.sh serve-api' for API docs at http://127.0.0.1:8001/"
    echo "📖 Terminal 2: Run './test_docs.sh serve-quarto' for Quarto docs at http://127.0.0.1:8002/"
}

# Function to build docs (strict mode)
build_api_docs_strict() {
    echo "🏗️  Building API documentation (strict mode)..."
    mkdocs build --strict
    if [ $? -eq 0 ]; then
        echo "✅ API documentation built successfully!"
        echo "📁 Built files are in: ./site/"
    else
        echo "❌ API documentation build failed!"
        return 1
    fi
}

# Function to clean build
clean_docs() {
    echo "🧹 Cleaning documentation builds..."
    rm -rf site/
    rm -rf docs/_book/
    rm -rf docs/.quarto/
    echo "✅ Clean complete!"
}

# Function to validate both sites
validate_all() {
    echo "🔍 Validating all documentation..."
    install_deps
    
    echo ""
    echo "=== Building MkDocs API Documentation ==="
    build_api_docs
    api_result=$?
    
    echo ""
    echo "=== Building Quarto Documentation ==="
    build_quarto_docs
    quarto_result=$?
    
    if [ $api_result -eq 0 ] && [ $quarto_result -eq 0 ]; then
        echo ""
        echo "🎉 All documentation built successfully!"
        echo "📁 API docs: ./site/"
        echo "📁 Quarto docs: ./docs/_book/"
        return 0
    else
        echo ""
        echo "❌ Some documentation builds failed!"
        return 1
    fi
}

# Parse command line arguments
case "${1:-help}" in
    "install")
        install_deps
        ;;
    "build-api")
        install_deps
        build_api_docs
        ;;
    "build-quarto")
        install_deps
        build_quarto_docs
        ;;
    "build-all")
        install_deps
        validate_all
        ;;
    "build-strict")
        install_deps
        build_api_docs_strict
        ;;
    "serve-api")
        install_deps
        build_api_docs
        serve_api_docs
        ;;
    "serve-quarto")
        install_deps
        build_quarto_docs
        serve_quarto_docs
        ;;
    "serve-both")
        serve_both_docs
        ;;
    "clean")
        clean_docs
        ;;
    "validate")
        validate_all
        ;;
    "help")
        echo "📋 Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  install       - Install documentation dependencies"
        echo "  build-api     - Build MkDocs API documentation only"
        echo "  build-quarto  - Build Quarto documentation only"
        echo "  build-all     - Build both documentation sites"
        echo "  build-strict  - Build API docs with strict mode (fails on warnings)"
        echo "  serve-api     - Build and serve API docs locally at :8001"
        echo "  serve-quarto  - Build and serve Quarto docs locally at :8002"
        echo "  serve-both    - Instructions to serve both simultaneously"
        echo "  clean         - Clean all build directories"
        echo "  validate      - Validate both documentation sites"
        echo "  help          - Show this help"
        echo ""
        echo "🌐 Sites will be available at:"
        echo "   API Documentation: http://127.0.0.1:8001/"
        echo "   Quarto Documentation: http://127.0.0.1:8002/"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "🆘 Use '$0 help' for usage information"
        exit 1
        ;;
esac
