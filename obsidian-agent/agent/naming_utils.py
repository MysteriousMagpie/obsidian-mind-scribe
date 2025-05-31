
"""Module for handling filename conventions and normalization."""

import re
from datetime import datetime
from pathlib import Path

import frontmatter


def get_conventional_name(note_path: Path, post: frontmatter.Post) -> str:
    """
    Generate a conventional filename based on date and content.
    
    Args:
        note_path: Current path to the note
        post: The frontmatter Post object
        
    Returns:
        Conventional filename
    """
    current_name = note_path.name
    
    # If using PARA structure, use PARA naming conventions
    if _is_para_vault():
        para_type = post.metadata.get('para_type', 'inbox')
        
        # For daily notes, ensure date prefix
        if para_type == 'daily':
            if re.match(r'^\d{4}-\d{2}-\d{2}--', current_name):
                return current_name
            
            # Get date and create proper daily note name
            date_str = post.metadata.get('date_created', datetime.now().strftime('%Y-%m-%d'))
            try:
                if isinstance(date_str, str):
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    date_obj = date_str
                date_prefix = date_obj.strftime('%Y-%m-%d')
            except:
                date_prefix = datetime.fromtimestamp(note_path.stat().st_mtime).strftime('%Y-%m-%d')
            
            return f"{date_prefix}--daily-note.md"
        
        # For other PARA types, use title case
        title = post.metadata.get('title', note_path.stem)
        normalized = re.sub(r'[^\w\s\-]', '', title)
        normalized = ' '.join(word.capitalize() for word in normalized.split())
        normalized = normalized.replace(' ', '_')
        
        return f"{normalized}.md"
    
    # Original naming logic for non-PARA vaults
    if re.match(r'^\d{4}-\d{2}-\d{2}--', current_name):
        return current_name
    
    # Get date from frontmatter or file mtime
    date_str = post.metadata.get('date')
    if date_str:
        try:
            if isinstance(date_str, str):
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = date_str
            date_prefix = date_obj.strftime('%Y-%m-%d')
        except:
            date_prefix = datetime.fromtimestamp(note_path.stat().st_mtime).strftime('%Y-%m-%d')
    else:
        date_prefix = datetime.fromtimestamp(note_path.stat().st_mtime).strftime('%Y-%m-%d')
    
    # Create slug from filename
    slug = re.sub(r'[^\w\-]', '-', note_path.stem.lower())
    slug = re.sub(r'-+', '-', slug).strip('-')
    
    return f"{date_prefix}--{slug}.md"


def _is_para_vault() -> bool:
    """Check if vault is using PARA structure."""
    from .config import config
    
    para_folders = ['00_Inbox', '01_Templates', '02_Projects', '03_Areas', '04_Resources']
    
    for folder in para_folders:
        if (config.vault_path / folder).exists():
            return True
    
    return False
