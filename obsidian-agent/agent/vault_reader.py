
"""Module for reading and filtering Obsidian vault files."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from .config import config


def get_observation_notes(days: int = 7) -> List[Path]:
    """
    Get observation note files from the last n days.
    
    Args:
        days: Number of days to look back for notes
        
    Returns:
        List of Path objects for observation note files
        
    Raises:
        ValueError: If vault path doesn't exist or observations folder not found
    """
    observations_path = config.vault_path / Path("3-Areas/Mind-Body-System/observations")
    
    if not observations_path.exists():
        raise ValueError(
            f"Observations folder not found: {observations_path}. "
            "Please check your vault structure."
        )
    
    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=days)
    
    observation_files = []
    
    # Walk through all markdown files in the observations directory
    for file_path in observations_path.rglob("*.md"):
        if file_path.is_file():
            # Get file modification time
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Include files modified within the specified days
            if mtime >= cutoff_date:
                observation_files.append(file_path)
    
    # Sort by modification time, newest first
    observation_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    return observation_files


def read_note_content(file_path: Path) -> str:
    """
    Read the content of a note file.
    
    Args:
        file_path: Path to the note file
        
    Returns:
        The content of the note as a string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback to latin-1 encoding if utf-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()
