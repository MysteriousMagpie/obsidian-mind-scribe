
"""Module for organizing files and determining correct folder locations."""

from pathlib import Path

import frontmatter

from .config import config


def get_correct_folder(post: frontmatter.Post, note_path: Path) -> Path:
    """
    Determine the correct folder for a note based on its type.
    
    Args:
        post: The frontmatter Post object
        note_path: Current path to the note
        
    Returns:
        Path to the correct folder
    """
    # If using PARA structure, use PARA folders
    if _is_para_vault():
        para_type = post.metadata.get('para_type', 'inbox')
        
        para_folders = {
            'inbox': '00_Inbox',
            'template': '01_Templates',
            'project': '02_Projects',
            'area': '03_Areas',
            'resource': '04_Resources',
            'daily': '05_Daily',
            'archive': '06_Archive'
        }
        
        target_folder = para_folders.get(para_type, '00_Inbox')
        target_path = config.vault_path / target_folder
        
        # Check if already in correct location
        try:
            note_path.relative_to(target_path)
            return note_path.parent
        except ValueError:
            return target_path
    
    # Original folder logic for non-PARA vaults
    note_type = post.metadata.get('type', 'note')
    
    type_folders = {
        'observation': '3-Areas/Mind-Body-System/observations',
        'hypothesis': '3-Areas/Mind-Body-System/hypotheses',
        'review': '3-Areas/Mind-Body-System/reviews',
        'project': '2-Projects',
        'note': '1-Inbox'
    }
    
    target_folder = type_folders.get(note_type, '1-Inbox')
    target_path = config.vault_path / target_folder
    
    # If already in correct location, return current folder
    try:
        note_path.relative_to(target_path)
        return note_path.parent
    except ValueError:
        return target_path


def _is_para_vault() -> bool:
    """Check if vault is using PARA structure."""
    para_folders = ['00_Inbox', '01_Templates', '02_Projects', '03_Areas', '04_Resources']
    
    for folder in para_folders:
        if (config.vault_path / folder).exists():
            return True
    
    return False
