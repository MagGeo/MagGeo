# MagGeo Documentation Guide

## Overview

MagGeo uses a simplified documentation approach with **MkDocs only**. 


## Documentation Structure

```
docs/                           # Main documentation directory
├── index.md                   # Homepage
├── about/                     # About pages
│   ├── changelog.md
│   ├── citation.md
│   └── CONTRIBUTING.md
├── api/                       # API Reference
│   ├── index.md
│   ├── core.md
│   ├── swarm_data_manager.md
│   ├── parallel_processing.md
│   └── indices.md
├── examples/                  # Examples and tutorials
│   ├── basic.md
│   └── advanced.md
├── getting-started/          # Getting started guides
│   ├── installation.md
│   └── quickstart.md
├── science-behind/           # Scientific background
│   ├── intro.md
│   ├── background.md
│   ├── calculation_mag_components.md
│   └── how_does_it_works.md
├── user-guide/              # User guides
│   └── basic-usage.md
├── images/                  # Documentation images
└── stylesheets/            # Custom styles
    └── extra.css
```

## Local Development

### Prerequisites

- Python 3.8+
- Git

### Setup and Testing

1. **Install dependencies:**
   ```bash
   ./test_docs.sh install
   ```

2. **Build documentation:**
   ```bash
   ./test_docs.sh build
   ```

3. **Serve locally for development:**
   ```bash
   ./test_docs.sh serve
   ```
   Documentation will be available at http://127.0.0.1:8000/

4. **Build with strict mode (recommended before pushing):**
   ```bash
   ./test_docs.sh build-strict
   ```

5. **Clean build files:**
   ```bash
   ./test_docs.sh clean
   ```

### Available Commands

| Command | Description |
|---------|-------------|
| `./test_docs.sh install` | Install documentation dependencies |
| `./test_docs.sh build` | Build MkDocs documentation |
| `./test_docs.sh build-strict` | Build docs with strict mode (fails on warnings) |
| `./test_docs.sh serve` | Build and serve docs locally at :8000 |
| `./test_docs.sh clean` | Clean build directory |
| `./test_docs.sh validate` | Validate documentation build |
| `./test_docs.sh help` | Show help information |

## Deployment

### Automatic Deployment

Documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch via the GitHub Actions workflow (`.github/workflows/deploy_combined_docs.yml`).

### Manual Deployment

If you need to deploy manually:

```bash
# Build the documentation
./test_docs.sh build-strict

# The built site will be in ./site/ directory
# You can then deploy this directory to your hosting service
```

## Configuration

### MkDocs Configuration

The main configuration is in `mkdocs.yml`:

- **Site Information**: Name, description, URL
- **Theme**: Material theme with custom colors and features
- **Navigation**: Page structure and organization
- **Plugins**: MkDocstrings for API docs, search, git revision dates
- **Extensions**: Python-Markdown extensions for enhanced formatting

### Key Configuration Sections

```yaml
# Site configuration
site_name: MagGeo Documentation
site_url: https://maggeo.github.io/MagGeo/
docs_dir: docs

# Theme and appearance
theme:
  name: material
  palette:
    - scheme: default
      primary: blue
      accent: amber

# API documentation
plugins:
  - mkdocstrings:
      handlers:
        python:
          paths: [.]
```

## Writing Documentation

### Content Guidelines

1. **Use clear, descriptive headings**
2. **Include code examples with syntax highlighting**
3. **Add cross-references between related sections**
4. **Keep content up-to-date with code changes**

### Markdown Features

MkDocs supports enhanced Markdown features:

- **Admonitions**: `!!! note`, `!!! warning`, `!!! tip`
- **Code blocks**: Syntax highlighting with language specification
- **Mathematics**: LaTeX math rendering with MathJax
- **Tabs**: Content in tabbed containers
- **Details**: Collapsible content sections

### API Documentation

API documentation is automatically generated from docstrings using MkDocstrings. Ensure your Python functions and classes have proper Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2

    Returns:
        Description of return value

    Examples:
        >>> example_function("test", 42)
        True
    """
    pass
```

## Troubleshooting

### Common Issues

1. **Build failures**: Check for broken links and missing files
2. **Import errors**: Ensure all dependencies are installed
3. **Styling issues**: Check custom CSS in `docs/stylesheets/extra.css`

### Getting Help

- Check the MkDocs documentation: https://www.mkdocs.org/
- Material theme docs: https://squidfunk.github.io/mkdocs-material/
- MkDocstrings plugin: https://mkdocstrings.github.io/
