"""
Configuration module for the config-service
"""
import os
import sys

# Get the absolute path to the microservices directory
current_dir = os.path.dirname(os.path.abspath(__file__))
microservices_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(microservices_dir)

# Add project root to sys.path so we can import microservices package
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Get the absolute path to the microservices directory
current_dir = os.path.dirname(os.path.abspath(__file__))
microservices_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(microservices_dir)

# Add project root to sys.path so we can import microservices package
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from microservices.app_config.config import (
    Service, 
    get_service_config, 
    get_database_config,
    namedtuple_to_connection_dict
)

# Global configuration instances
env = os.environ
service_config = get_service_config(env, Service.CONFIG)
db_config = namedtuple_to_connection_dict(get_database_config(env, Service.CONFIG))
