# openbca/config.py
"""
Centralized configuration for OpenBCA.
Handles path resolution for various directories used in the project.
"""
import sys
from pathlib import Path


# Use functions that return pathlib objects rather than module level constants
# Ensures serializability by sqlmesh

def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_core_project_dir() -> Path:
    return get_repo_root() / 'core'


def get_nspm_project_dir() -> Path:
    return get_repo_root() / 'nspm'


def get_streamlit_app_dir() -> Path:
    return get_repo_root() / 'streamlit_test'


def get_input_templates_dir() -> Path:
    return get_nspm_project_dir() / 'input_templates'


def get_output_dir() -> Path:
    output_dir = get_repo_root() / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_logs_dir() -> Path:
    logs_dir = get_repo_root() / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir
