# MagGeo Documentation

This directory contains the MkDocs-based API documentation for MagGeo.

## Structure

```
api_docs/              # Documentation source files
├── about/            # About pages (changelog, citation, etc.)
├── api/              # API reference documentation  
├── examples/         # Usage examples
├── getting-started/  # Installation and quickstart guides
├── user-guide/       # User guide documentation
├── javascripts/      # Custom JavaScript files
├── stylesheets/      # Custom CSS files
└── index.md          # Home page

mkdocs.yml            # MkDocs configuration file
test_docs.sh          # Local testing script
```

## Local Testing

### Quick Start

Run the test script to build and serve the documentation locally:

```bash
./test_docs.sh
```

This will:
1. Create a virtual environment (if needed)
2. Install dependencies
3. Build the documentation
4. Start a local server at http://127.0.0.1:8001/

### Manual Testing

If you prefer to run commands manually:

```bash
# Create and activate virtual environment
python3 -m venv docs_env
source docs_env/bin/activate

# Install dependencies
pip install -e ".[docs]"

# Build documentation
mkdocs build

# Serve locally
mkdocs serve --dev-addr 127.0.0.1:8001
```

### Available Commands

```bash
./test_docs.sh serve    # Build and serve (default)
./test_docs.sh build    # Build only
./test_docs.sh clean    # Clean build directory
./test_docs.sh help     # Show help
```

## Configuration

The documentation is configured in `mkdocs.yml`:

- **docs_dir**: `api_docs` - Points to the documentation source
- **site_dir**: `site` - Output directory for built documentation
- **theme**: Material Design theme with custom styling
- **plugins**: mkdocstrings for API documentation generation

## GitHub Actions

The documentation is automatically built and deployed via GitHub Actions:

- **Trigger**: Push to `main`, `develop`, or `refactor_maggeo` branches
- **Build**: Runs `mkdocs build --strict` to catch any issues
- **Deploy**: Automatically deploys to GitHub Pages on push to `main`

## Separate from Quarto Site

This MkDocs site (`api_docs/`) is separate from any Quarto documentation that may exist in a `docs/` folder. This allows you to:

- Maintain API documentation with MkDocs (better for Python APIs)
- Use Quarto for research documentation and analysis
- Keep different documentation types organized

## Troubleshooting

### Common Issues

1. **Port already in use**: Use a different port with `--dev-addr 127.0.0.1:8002`
2. **Missing files warnings**: These are informational; the build will still succeed
3. **Python environment**: Make sure to use Python 3.8+ with the docs dependencies

### Dependencies

The documentation requires these packages (defined in `pyproject.toml`):

- mkdocs>=1.5.0
- mkdocs-material>=9.4.0
- mkdocstrings[python]>=0.24.0
- mkdocs-jupyter>=0.24.0
- mkdocs-git-revision-date-localized-plugin>=1.2.0
- mkdocs-awesome-pages-plugin>=2.9.0
