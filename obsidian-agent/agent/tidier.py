
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
    
    # Add PARA-specific fields if using PARA structure
    if _is_para_vault():
        if 'para_type' not in post.metadata:
            post.metadata['para_type'] = infer_para_type_basic(post.content, note_path)
            modified = True
        
        if 'last_modified' not in post.metadata:
            post.metadata['last_modified'] = datetime.now().strftime('%Y-%m-%d')
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


def _save_note(note_path: Path, post: frontmatter.Post) -> None:
    """
    Save a frontmatter Post back to file.
    
    Args:
        note_path: Path to save the file
        post: The frontmatter Post object to save
    """
    with open(note_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(post))
