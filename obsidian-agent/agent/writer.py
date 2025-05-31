
"""Module for writing weekly review files back to the Obsidian vault."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import config


def write_weekly_review(markdown: str, date_str: Optional[str] = None) -> Path:
    """
    Write a weekly review markdown file to the vault.
    
    Args:
        markdown: The markdown content to write
        date_str: Optional date string. If not provided, uses current date
        
    Returns:
        Path to the written file
        
    Raises:
        OSError: If unable to create directories or write file
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Create the reviews directory path
    reviews_path = config.vault_path / "3-Areas" / "Mind-Body-System" / "reviews"
    
    # Ensure the directory exists
    reviews_path.mkdir(parents=True, exist_ok=True)
    
    # Create the filename
    filename = f"weekly-review--{date_str}.md"
    file_path = reviews_path / filename
    
    try:
        # Write the markdown content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"✓ Weekly review written to: {file_path}")
        return file_path
        
    except Exception as e:
        raise OSError(f"Failed to write weekly review to {file_path}: {str(e)}")


def ensure_vault_structure() -> None:
    """
    Ensure the required vault directory structure exists.
    
    Raises:
        OSError: If unable to create required directories
    """
    required_paths = [
        config.vault_path / "3-Areas" / "Mind-Body-System" / "observations",
        config.vault_path / "3-Areas" / "Mind-Body-System" / "reviews"
    ]
    
    for path in required_paths:
        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Ensured directory exists: {path}")
        except Exception as e:
            raise OSError(f"Failed to create directory {path}: {str(e)}")
