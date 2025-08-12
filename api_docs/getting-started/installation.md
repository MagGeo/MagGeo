# Installation

MagGeo requires Python 3.8 or higher and can be installed via pip or from source.

## Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **VirES Token**: Required for downloading Swarm data (free registration)

## Install from PyPI (Recommended)

```bash
pip install maggeo
```

For development features:

```bash
pip install "maggeo[dev]"
```

For documentation building:

```bash
pip install "maggeo[docs]"
```

## Install from Source

For the latest development version:

```bash
git clone https://github.com/fbenitez92/maggeo.git
cd maggeo
pip install -e ".[dev]"
```

## Get Your VirES Token

!!! warning "Token Required"
    You need a VirES token to download Swarm satellite data.

1. Go to [VirES for Swarm](https://vires.services/)
2. Click "Sign up" and create a free account
3. After login, go to your profile to find your access token
4. Copy the token for use in MagGeo

## Verify Installation

Test your installation:

```python
import maggeo
print(f"MagGeo version: {maggeo.__version__}")

# Test basic functionality
from maggeo import SwarmDataManager
manager = SwarmDataManager("test_data")
print("✅ MagGeo installed successfully!")
```

## Troubleshooting

### Common Issues

!!! failure "ImportError: No module named 'maggeo'"
    **Solution**: Make sure you activated the correct Python environment where MagGeo is installed.

!!! failure "Token authentication failed"
    **Solution**: Check that your VirES token is correct and your account is active.

!!! failure "Permission denied when writing files"
    **Solution**: Ensure you have write permissions to your data directory.

## Next Steps

- [Quick Start Guide](quickstart.md) - Get up and running in 5 minutes
- [Basic Usage](../user-guide/basic-usage.md) - Learn the fundamentals
- [Examples](../examples/basic.md) - See MagGeo in action