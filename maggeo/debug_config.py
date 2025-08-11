"""
Configuration-based debug system for MagGeo.
"""
import yaml
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class DebugConfig:
    """Debug configuration settings."""
    enabled: bool = False
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    save_temp_files: bool = False
    temp_dir: str = "temp_data"
    log_file: str = "maggeo.log"
    
    # Specific debug options
    log_parameters: bool = True
    log_gps_data: bool = True
    log_swarm_data: bool = True
    log_interpolation: bool = True
    log_chaos_values: bool = True
    
    # File saving options
    save_gps_data: bool = True
    save_swarm_data: bool = True
    save_interpolation: bool = True
    save_chaos_results: bool = True

def load_debug_config(config_path: Optional[str] = None) -> DebugConfig:
    """Load debug configuration from YAML file or use defaults."""
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f).get('debug', {})
        return DebugConfig(**config_dict)
    return DebugConfig()

def create_debug_config_template(output_path: str = "debug_config.yml"):
    """Create a template debug configuration file."""
    template = {
        'debug': {
            'enabled': False,
            'log_level': 'INFO',
            'save_temp_files': False,
            'temp_dir': 'temp_data',
            'log_file': 'maggeo.log',
            'log_parameters': True,
            'log_gps_data': True,
            'log_swarm_data': True,
            'log_interpolation': True,
            'log_chaos_values': True,
            'save_gps_data': True,
            'save_swarm_data': True,
            'save_interpolation': True,
            'save_chaos_results': True
        }
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(template, f, default_flow_style=False, indent=2)
    
    print(f"Debug configuration template created at: {output_path}")
    print("Edit this file and set 'enabled: true' to activate debug mode.")

if __name__ == "__main__":
    create_debug_config_template()
