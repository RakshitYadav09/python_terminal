"""
Error handling utilities for Python Terminal.
"""

def format_error(command_name: str, error: Exception) -> str:
    """Format an error message for commands."""
    return f"{command_name}: {error}"
