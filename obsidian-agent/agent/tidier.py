
"""Module for tidying and organizing Obsidian vault files."""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import frontmatter

from .config import config


def tidy_vault(dry_run: bool = False) -> Dict[str, int]:
    """
    Tidy the entire Obsidian vault by organizing markdown files.
    
    Args:
        dry_run: If True, only report what would be done without making changes
        
    Returns:
        Dictionary with counts of different operations performed
    """
    if not config.vault_path.exists():
        raise ValueError(f"Vault path does not exist: {config.vault_path}")
    
    stats = {
        'files_processed': 0,
        'frontmatter_added': 0,
        'files_moved': 0,
        'files_renamed': 0,
        'tags_normalized': 0,
        'errors': 0
    }
    
    print(f"🔍 Scanning vault: {config.vault_path}")
    if dry_run:
        print("🧪 DRY RUN MODE - No files will be modified")
    
    # Walk through all markdown files in the vault
    for md_file in config.vault_path.rglob("*.md"):
        if md_file.is_file():
            try:
                stats['files_processed'] += 1
                changes = process_note_file(md_file, dry_run)
                
                # Update stats
                for key, value in changes.items():
                    if key in stats:
                        stats[key] += value
                        
            except Exception as e:
                print(f"❌ Error processing {md_file}: {e}")
                stats['errors'] += 1
    
    return stats


def process_note_file(note_path: Path, dry_run: bool = False) -> Dict[str, int]:
    """
    Process a single note file and apply tidying operations.
    
    Args:
        note_path: Path to the markdown file
        dry_run: If True, only report what would be done
        
    Returns:
        Dictionary with counts of operations performed on this file
    """
    changes = {
        'frontmatter_added': 0,
        'files_moved': 0,
        'files_renamed': 0,
        'tags_normalized': 0
    }
    
    try:
        # Read the file
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse frontmatter
        post = frontmatter.loads(content)
        original_metadata = post.metadata.copy()
        
        # Ensure frontmatter exists
        if ensure_frontmatter(post, note_path):
            changes['frontmatter_added'] = 1
            if not dry_run:
                _save_note(note_path, post)
            else:
                print(f"  📝 Would add frontmatter to: {note_path.name}")
        
        # Normalize tags
        if normalize_tags(post):
            changes['tags_normalized'] = 1
            if not dry_run:
                _save_note(note_path, post)
            else:
                print(f"  🏷️  Would normalize tags in: {note_path.name}")
        
        # Check if file needs renaming
        new_name = get_conventional_name(note_path, post)
        if new_name != note_path.name:
            changes['files_renamed'] = 1
            if not dry_run:
                new_path = note_path.parent / new_name
                note_path.rename(new_path)
                note_path = new_path
            else:
                print(f"  📄 Would rename: {note_path.name} → {new_name}")
        
        # Check if file needs moving
        correct_folder = get_correct_folder(post, note_path)
        if correct_folder != note_path.parent:
            changes['files_moved'] = 1
            if not dry_run:
                correct_folder.mkdir(parents=True, exist_ok=True)
                new_path = correct_folder / note_path.name
                note_path.rename(new_path)
            else:
                rel_old = note_path.relative_to(config.vault_path)
                rel_new = correct_folder.relative_to(config.vault_path) / note_path.name
                print(f"  📁 Would move: {rel_old} → {rel_new}")
                
    except Exception as e:
        print(f"❌ Error processing {note_path}: {e}")
        raise
    
    return changes


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
    content_tags = re.findall(r'#(\w+)', post.content)
    
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
    
    # If already has date prefix, keep it
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


def get_correct_folder(post: frontmatter.Post, note_path: Path) -> Path:
    """
    Determine the correct folder for a note based on its type.
    
    Args:
        post: The frontmatter Post object
        note_path: Current path to the note
        
    Returns:
        Path to the correct folder
    """
    note_type = post.metadata.get('type', 'note')
    
    # Define type to folder mapping
    type_folders = {
        'observation': '3-Areas/Mind-Body-System/observations',
        'hypothesis': '3-Areas/Mind-Body-System/hypotheses',
        'review': '3-Areas/Mind-Body-System/reviews',
        'project': '2-Projects',
        'note': '1-Inbox'  # Default location for generic notes
    }
    
    target_folder = type_folders.get(note_type, '1-Inbox')
    target_path = config.vault_path / target_folder
    
    # If already in correct location, return current folder
    try:
        note_path.relative_to(target_path)
        return note_path.parent
    except ValueError:
        # Not in target folder, return target
        return target_path


def _save_note(note_path: Path, post: frontmatter.Post) -> None:
    """
    Save a frontmatter Post back to file.
    
    Args:
        note_path: Path to save the file
        post: The frontmatter Post object to save
    """
    with open(note_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(post))
