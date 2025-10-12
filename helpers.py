"""
Helper functions for GoSubtitle application.

Provides utility functions for file validation, time conversion,
and other common operations.
"""

import os
from pathlib import Path
from typing import Optional


def validate_xml_file(file_path: str) -> bool:
    """
    Validate that a file exists and has .xml extension.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if file is valid, False otherwise
    """
    if not file_path:
        return False
    
    path = Path(file_path)
    return path.exists() and path.suffix.lower() == '.xml'


def validate_srt_path(file_path: str) -> bool:
    """
    Validate that a save path is valid for SRT files.
    
    Args:
        file_path: Path where the SRT file will be saved
        
    Returns:
        True if path is valid, False otherwise
    """
    if not file_path:
        return False
    
    path = Path(file_path)
    
    # Check if directory exists (or can be created)
    parent_dir = path.parent
    if not parent_dir.exists():
        return False
    
    # Ensure .srt extension
    return path.suffix.lower() == '.srt'


def ensure_srt_extension(file_path: str) -> str:
    """
    Ensure a file path has the .srt extension.
    
    Args:
        file_path: Original file path
        
    Returns:
        File path with .srt extension
    """
    path = Path(file_path)
    if path.suffix.lower() != '.srt':
        return str(path.with_suffix('.srt'))
    return file_path


def format_duration(frames: float, fps: int = 24) -> str:
    """
    Format a duration in frames as a human-readable string.
    
    Args:
        frames: Duration in frames
        fps: Frames per second
        
    Returns:
        Formatted duration string (e.g., "1h 23m 45s")
    """
    seconds = frames / fps
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    
    return " ".join(parts)


def get_project_directory() -> Path:
    """
    Get the root directory of the project.
    
    Returns:
        Path to the project root directory
    """
    return Path(__file__).resolve().parent


def get_ui_directory() -> Path:
    """
    Get the UI directory path.
    
    Returns:
        Path to the UI directory
    """
    return get_project_directory() / "ui"
