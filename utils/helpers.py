"""
Helper functions for file system operations.
"""
import os
from .error_handler import format_error


def safe_listdir(path: str):
    """List directory contents, returning error message on failure."""
    try:
        return os.listdir(path)
    except Exception as e:
        return format_error('ls', e)
