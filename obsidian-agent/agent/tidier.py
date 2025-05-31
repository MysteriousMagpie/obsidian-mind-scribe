
"""Module for tidying and organizing Obsidian vault files."""

from pathlib import Path
from typing import Dict

import frontmatter

from .config import config
from .frontmatter_handler import ensure_frontmatter, normalize_tags
from .file_organizer import get_correct_folder
from .naming_utils import get_conventional_name


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


def _save_note(note_path: Path, post: frontmatter.Post) -> None:
    """
    Save a frontmatter Post back to file.
    
    Args:
        note_path: Path to save the file
        post: The frontmatter Post object to save
    """
    with open(note_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(post))
