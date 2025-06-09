
"""Module for handling frontmatter operations in Obsidian notes."""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict

import frontmatter

from .config import config


def ensure_frontmatter(post: frontmatter.Post, note_path: Path) -> bool:
    """
    Ensure the note has valid frontmatter with required fields.
    
    Args:
        post: The frontmatter Post object
        note_path: Path to the note file
        
    Returns:
        True if frontmatter was added/modified, False otherwise
    """
    modified = False
    
    # Check if we need to add basic frontmatter
    if not post.metadata:
        modified = True
    
    # Ensure required fields exist
    if 'type' not in post.metadata:
        post.metadata['type'] = infer_type_from_content(post.content, note_path)
        modified = True
    
    if 'status' not in post.metadata:
        post.metadata['status'] = 'active'
        modified = True
    
    if 'tags' not in post.metadata:
        post.metadata['tags'] = []
        modified = True
    
    # Add PARA-specific fields if using PARA structure
    if _is_para_vault():
        if 'para_type' not in post.metadata:
            post.metadata['para_type'] = infer_para_type_basic(post.content, note_path)
            modified = True
        
        if 'last_modified' not in post.metadata:
            post.metadata['last_modified'] = datetime.now().strftime('%Y-%m-%d')
            modified = True
    
    return modified


def normalize_tags(post: frontmatter.Post) -> bool:
    """
    Normalize tags to ensure they're in frontmatter as a proper list.
    
    Args:
        post: The frontmatter Post object
        
    Returns:
        True if tags were modified, False otherwise
    """
    modified = False
    
    # Extract tags from content (hashtags)
    # Support hyphenated tags like #time-management
    content_tags = re.findall(r'#([\w-]+)', post.content)
    
    # Get existing frontmatter tags
    fm_tags = post.metadata.get('tags', [])
    if isinstance(fm_tags, str):
        fm_tags = [fm_tags]
    elif not isinstance(fm_tags, list):
        fm_tags = []
    
    # Combine and deduplicate
    all_tags = list(set(fm_tags + content_tags))
    
    # Update if different
    if set(all_tags) != set(fm_tags):
        post.metadata['tags'] = sorted(all_tags)
        modified = True
    
    return modified


def infer_type_from_content(content: str, note_path: Path) -> str:
    """
    Infer the note type based on content, filename, and folder location.
    
    Args:
        content: The note content
        note_path: Path to the note file
        
    Returns:
        Inferred type string
    """
    # Check folder structure for hints
    path_parts = note_path.parts
    if 'observations' in path_parts:
        return 'observation'
    elif 'hypotheses' in path_parts:
        return 'hypothesis'
    elif 'reviews' in path_parts:
        return 'review'
    elif 'projects' in path_parts:
        return 'project'
    
    # Check filename patterns
    filename = note_path.stem.lower()
    if 'observation' in filename or 'obs' in filename:
        return 'observation'
    elif 'hypothesis' in filename or 'hyp' in filename:
        return 'hypothesis'
    elif 'review' in filename:
        return 'review'
    elif 'project' in filename:
        return 'project'
    
    # Check content patterns
    content_lower = content.lower()
    if any(phrase in content_lower for phrase in ['i observed', 'noticed that', 'observation:']):
        return 'observation'
    elif any(phrase in content_lower for phrase in ['hypothesis:', 'i think', 'theory:']):
        return 'hypothesis'
    elif any(phrase in content_lower for phrase in ['weekly review', 'summary', 'reflection']):
        return 'review'
    
    # Default fallback
    return 'note'


def infer_para_type_basic(content: str, note_path: Path) -> str:
    """
    Basic PARA type inference for tidier module.
    
    Args:
        content: The note content
        note_path: Path to the note file
        
    Returns:
        Inferred PARA type string
    """
    filename = note_path.stem.lower()
    content_lower = content.lower()
    
    # Check for daily notes
    if re.match(r'^\d{4}-\d{2}-\d{2}', filename):
        return 'daily'
    
    # Check for common patterns
    if any(keyword in filename for keyword in ['project', 'proj']):
        return 'project'
    elif any(keyword in filename for keyword in ['daily', 'journal']):
        return 'daily'
    elif any(keyword in filename for keyword in ['guide', 'reference', 'resource']):
        return 'resource'
    elif any(keyword in filename for keyword in ['area', 'responsibility']):
        return 'area'
    
    # Check content
    if any(phrase in content_lower for phrase in ['project:', 'deadline:', 'deliverable:']):
        return 'project'
    elif any(phrase in content_lower for phrase in ['daily note', 'today i']):
        return 'daily'
    elif any(phrase in content_lower for phrase in ['reference', 'guide:', 'tutorial:']):
        return 'resource'
    elif any(phrase in content_lower for phrase in ['ongoing', 'responsibility']):
        return 'area'
    
    return 'inbox'


def _is_para_vault() -> bool:
    """Check if vault is using PARA structure."""
    para_folders = ['00_Inbox', '01_Templates', '02_Projects', '03_Areas', '04_Resources']
    
    for folder in para_folders:
        if (config.vault_path / folder).exists():
            return True
    
    return False
