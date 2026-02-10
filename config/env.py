# config/env.py
import os
from dotenv import load_dotenv
from pathlib import Path

from config.paths import get_repo_root, get_output_dir, get_logs_dir

def setup_env_vars():
    """Set up environment variables for SQLMesh."""
    repo_root = get_repo_root()

    # Load environment variables from .env file if it exists
    dotenv_path = repo_root / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
    
    # Set default values for environment variables if they are not already set
    if 'DB' not in os.environ:
        os.environ['DB'] = str(get_output_dir() / 'openbca.db')
    
    if 'DBV' not in os.environ:
        os.environ['DBV'] = str(get_output_dir() / 'openbca_input_validation.db')