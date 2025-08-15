#!/usr/bin/env python3
"""
Configuration examples for ANYmal Inspection Data Download
Shows different ways to securely configure credentials and settings
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
import configparser

class ANYmalConfig:
    """Configuration manager for ANYmal API credentials and settings"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file
        self.config = {}
        
    def load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        return {
            'server_url': os.getenv('ANYMAL_SERVER_URL'),
            'email': os.getenv('ANYMAL_EMAIL'),
            'password': os.getenv('ANYMAL_PASSWORD'),
            'verify_ssl': os.getenv('ANYMAL_VERIFY_SSL', 'true').lower() == 'true',
            'timeout': int(os.getenv('ANYMAL_TIMEOUT', '30')),
            'output_dir': os.getenv('ANYMAL_OUTPUT_DIR', './downloads')
        }
    
    def load_from_json(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def load_from_ini(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from INI file"""
        config = configparser.ConfigParser()
        config.read(config_file)
        
        if 'anymal' not in config:
            raise ValueError("Missing [anymal] section in config file")
            
        section = config['anymal']
        return {
            'server_url': section.get('server_url'),
            'email': section.get('email'),
            'password': section.get('password'),
            'verify_ssl': section.getboolean('verify_ssl', True),
            'timeout': section.getint('timeout', 30),
            'output_dir': section.get('output_dir', './downloads')
        }
    
    def create_sample_configs(self):
        """Create sample configuration files"""
        
        # Sample JSON config
        json_config = {
            "server_url": "your-server.com",
            "email": "your-email@domain.com", 
            "password": "your-password",
            "verify_ssl": True,
            "timeout": 30,
            "output_dir": "./downloads"
        }
        
        with open('anymal_config.json.example', 'w') as f:
            json.dump(json_config, f, indent=2)
        
        # Sample INI config
        ini_content = """[anymal]
server_url = your-server.com
email = your-email@domain.com
password = your-password
verify_ssl = true
timeout = 30
output_dir = ./downloads
"""
        
        with open('anymal_config.ini.example', 'w') as f:
            f.write(ini_content)
        
        # Sample environment file
        env_content = """# ANYmal API Configuration
# Copy this to .env and update with your credentials

ANYMAL_SERVER_URL=your-server.com
ANYMAL_EMAIL=your-email@domain.com
ANYMAL_PASSWORD=your-password
ANYMAL_VERIFY_SSL=true
ANYMAL_TIMEOUT=30
ANYMAL_OUTPUT_DIR=./downloads
"""
        
        with open('.env.example', 'w') as f:
            f.write(env_content)
        
        print("Sample configuration files created:")
        print("- anymal_config.json.example")
        print("- anymal_config.ini.example") 
        print("- .env.example")


def load_config_with_fallback() -> Dict[str, Any]:
    """
    Load configuration with fallback priority:
    1. Environment variables
    2. anymal_config.json
    3. anymal_config.ini
    4. Default values
    """
    config_manager = ANYmalConfig()
    
    # Try environment variables first
    config = config_manager.load_from_env()
    if all(config[key] for key in ['server_url', 'email', 'password']):
        print("Using configuration from environment variables")
        return config
    
    # Try JSON config file
    if Path('anymal_config.json').exists():
        try:
            config = config_manager.load_from_json('anymal_config.json')
            print("Using configuration from anymal_config.json")
            return config
        except Exception as e:
            print(f"Failed to load JSON config: {e}")
    
    # Try INI config file
    if Path('anymal_config.ini').exists():
        try:
            config = config_manager.load_from_ini('anymal_config.ini')
            print("Using configuration from anymal_config.ini")
            return config
        except Exception as e:
            print(f"Failed to load INI config: {e}")
    
    # No valid config found
    raise ValueError("No valid configuration found. Please set environment variables or create a config file.")


if __name__ == "__main__":
    # Create sample configuration files
    config_manager = ANYmalConfig()
    config_manager.create_sample_configs()