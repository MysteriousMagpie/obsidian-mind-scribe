
"""Module for migrating Obsidian vault to PARA methodology structure."""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import frontmatter

from .config import config
from .link_manager import scan_and_update_links
from .templates import create_templates


def migrate_to_para(dry_run: bool = False) -> Dict[str, int]:
    """
    Complete migration of vault to PARA methodology structure.
    
    Args:
        dry_run: If True, only report what would be done
        
    Returns:
        Dictionary with counts of operations performed
    """
    print("🚀 Starting PARA methodology migration...")
    
    if dry_run:
        print("🧪 DRY RUN MODE - No files will be modified")
    
    stats = {
        'files_processed': 0,
        'folders_created': 0,
        'files_moved': 0,
        'files_renamed': 0,
        'frontmatter_updated': 0,
        'templates_created': 0,
        'links_updated': 0,
        'errors': 0
    }
    
    try:
        # Step 1: Create PARA folder structure
        folder_stats = create_para_structure(dry_run)
        stats.update(folder_stats)
        
        # Step 2: Create templates
        if not dry_run:
            templates = create_templates()
            stats['templates_created'] = len(templates)
        else:
            print("🗂️  Would create 5 PARA methodology templates")
            stats['templates_created'] = 5
        
        # Step 3: Process all markdown files
        file_moves = {}  # Track file movements for link updates
        
        for md_file in config.vault_path.rglob("*.md"):
            if md_file.is_file() and not _is_template_file(md_file):
                try:
                    stats['files_processed'] += 1
                    file_stats, old_path, new_path = process_para_file(md_file, dry_run)
                    
                    # Update stats
                    for key, value in file_stats.items():
                        if key in stats:
                            stats[key] += value
                    
                    # Track file moves for link updates
                    if old_path != new_path:
                        file_moves[old_path] = new_path
                        
                except Exception as e:
                    print(f"❌ Error processing {md_file}: {e}")
                    stats['errors'] += 1
        
        # Step 4: Update wikilinks
        if file_moves:
            print(f"🔗 Updating wikilinks for {len(file_moves)} moved files...")
            link_stats = scan_and_update_links(file_moves, dry_run)
            stats['links_updated'] = link_stats['links_updated']
        
        print(f"\n✅ PARA migration {'simulation' if dry_run else 'completed'}!")
        
    except Exception as e:
        print(f"❌ Critical error during migration: {e}")
        stats['errors'] += 1
    
    return stats


def create_para_structure(dry_run: bool = False) -> Dict[str, int]:
    """Create the PARA folder structure."""
    para_folders = [
        "00_Inbox",
        "01_Templates", 
        "02_Projects",
        "03_Areas",
        "04_Resources",
        "05_Daily",
        "06_Archive"
    ]
    
    # Common subfolders
    area_subfolders = [
        "03_Areas/Personal",
        "03_Areas/School",
        "03_Areas/Work",
        "03_Areas/Health",
        "03_Areas/Finance"
    ]
    
    resource_subfolders = [
        "04_Resources/Reference",
        "04_Resources/Guides",
        "04_Resources/Tools",
        "04_Resources/Learning"
    ]
    
    all_folders = para_folders + area_subfolders + resource_subfolders
    folders_created = 0
    
    for folder in all_folders:
        folder_path = config.vault_path / folder
        
        if not folder_path.exists():
            if not dry_run:
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"📁 Created folder: {folder}")
            else:
                print(f"📁 Would create folder: {folder}")
            folders_created += 1
    
    return {'folders_created': folders_created}


def process_para_file(file_path: Path, dry_run: bool = False) -> Tuple[Dict[str, int], Path, Path]:
    """
    Process a single file for PARA migration.
    
    Returns:
        (stats_dict, original_path, final_path)
    """
    stats = {
        'frontmatter_updated': 0,
        'files_moved': 0,
        'files_renamed': 0
    }
    
    original_path = file_path
    current_path = file_path
    
    try:
        # Read and parse file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        post = frontmatter.loads(content)
        
        # Update frontmatter for PARA
        if update_para_frontmatter(post, file_path):
            stats['frontmatter_updated'] = 1
            if not dry_run:
                _save_post(current_path, post)
        
        # Determine PARA type and correct location
        para_type = post.metadata.get('para_type', infer_para_type(post.content, file_path))
        correct_folder = get_para_folder(para_type, file_path, post)
        
        # Check if file needs moving
        if correct_folder != current_path.parent:
            stats['files_moved'] = 1
            if not dry_run:
                correct_folder.mkdir(parents=True, exist_ok=True)
                new_path = correct_folder / current_path.name
                current_path.rename(new_path)
                current_path = new_path
            else:
                rel_old = current_path.relative_to(config.vault_path)
                rel_new = correct_folder.relative_to(config.vault_path) / current_path.name
                print(f"  📁 Would move: {rel_old} → {rel_new}")
        
        # Check if file needs renaming
        conventional_name = get_para_conventional_name(current_path, post)
        if conventional_name != current_path.name:
            stats['files_renamed'] = 1
            if not dry_run:
                final_path = current_path.parent / conventional_name
                current_path.rename(final_path)
                current_path = final_path
            else:
                print(f"  📄 Would rename: {current_path.name} → {conventional_name}")
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
    
    return stats, original_path, current_path


def infer_para_type(content: str, file_path: Path) -> str:
    """
    Infer PARA type from content, filename, and folder location.
    """
    path_str = str(file_path).lower()
    content_lower = content.lower()
    filename = file_path.stem.lower()
    
    # Check for daily notes (date patterns)
    if re.match(r'^\d{4}-\d{2}-\d{2}', filename):
        return 'daily'
    
    # Check folder patterns for legacy migration
    if any(pattern in path_str for pattern in ['personal/', 'personal\\', '/personal']):
        return 'area'
    elif any(pattern in path_str for pattern in ['school/', 'school\\', '/school']):
        return 'area'
    elif any(pattern in path_str for pattern in ['guides/', 'guides\\', '/guides', 'resources/', 'resources\\', '/resources']):
        return 'resource'
    elif any(pattern in path_str for pattern in ['projects/', 'projects\\', '/projects']):
        return 'project'
    elif any(pattern in path_str for pattern in ['daily/', 'daily\\', '/daily', 'journal/', 'journal\\', '/journal']):
        return 'daily'
    
    # Check filename patterns
    if any(keyword in filename for keyword in ['project', 'proj']):
        return 'project'
    elif any(keyword in filename for keyword in ['daily', 'journal', 'log']):
        return 'daily'
    elif any(keyword in filename for keyword in ['guide', 'reference', 'resource', 'manual', 'tutorial']):
        return 'resource'
    elif any(keyword in filename for keyword in ['area', 'responsibility']):
        return 'area'
    
    # Check content patterns
    if any(phrase in content_lower for phrase in ['project:', 'deadline:', 'deliverable:', 'milestone:']):
        return 'project'
    elif any(phrase in content_lower for phrase in ['daily note', 'today i', 'morning', 'evening reflection']):
        return 'daily'
    elif any(phrase in content_lower for phrase in ['reference', 'guide:', 'tutorial:', 'how to', 'documentation']):
        return 'resource'
    elif any(phrase in content_lower for phrase in ['ongoing', 'responsibility', 'maintain', 'standard:']):
        return 'area'
    
    # Default to inbox for unclassified notes
    return 'inbox'


def get_para_folder(para_type: str, file_path: Path, post: frontmatter.Post) -> Path:
    """Get the correct PARA folder for a given type and context."""
    base_folders = {
        'inbox': '00_Inbox',
        'template': '01_Templates',
        'project': '02_Projects',
        'area': '03_Areas',
        'resource': '04_Resources',
        'daily': '05_Daily',
        'archive': '06_Archive'
    }
    
    base_folder = base_folders.get(para_type, '00_Inbox')
    
    # Handle specific subfolder logic
    if para_type == 'area':
        # Try to determine area category from path or content
        path_str = str(file_path).lower()
        if 'personal' in path_str:
            return config.vault_path / "03_Areas" / "Personal"
        elif 'school' in path_str:
            return config.vault_path / "03_Areas" / "School"
        elif 'work' in path_str:
            return config.vault_path / "03_Areas" / "Work"
        else:
            return config.vault_path / "03_Areas"
    
    elif para_type == 'resource':
        # Try to determine resource category
        path_str = str(file_path).lower()
        content = post.content.lower()
        
        if any(term in path_str or term in content for term in ['guide', 'tutorial', 'how-to']):
            return config.vault_path / "04_Resources" / "Guides"
        elif any(term in path_str or term in content for term in ['tool', 'software', 'app']):
            return config.vault_path / "04_Resources" / "Tools"
        elif any(term in path_str or term in content for term in ['learn', 'course', 'study']):
            return config.vault_path / "04_Resources" / "Learning"
        else:
            return config.vault_path / "04_Resources" / "Reference"
    
    return config.vault_path / base_folder


def update_para_frontmatter(post: frontmatter.Post, file_path: Path) -> bool:
    """Update frontmatter with PARA-specific fields."""
    modified = False
    
    # Ensure basic PARA fields exist
    if 'para_type' not in post.metadata:
        post.metadata['para_type'] = infer_para_type(post.content, file_path)
        modified = True
    
    if 'status' not in post.metadata:
        post.metadata['status'] = 'active'
        modified = True
    
    if 'tags' not in post.metadata:
        post.metadata['tags'] = []
        modified = True
    
    if 'last_modified' not in post.metadata:
        post.metadata['last_modified'] = datetime.now().strftime('%Y-%m-%d')
        modified = True
    
    # Add type-specific fields
    para_type = post.metadata.get('para_type', 'inbox')
    
    if para_type == 'project':
        if 'priority' not in post.metadata:
            post.metadata['priority'] = 'medium'
            modified = True
        if 'deadline' not in post.metadata:
            post.metadata['deadline'] = ''
            modified = True
    
    elif para_type == 'area':
        if 'last_reviewed' not in post.metadata:
            post.metadata['last_reviewed'] = datetime.now().strftime('%Y-%m-%d')
            modified = True
        if 'review_frequency' not in post.metadata:
            post.metadata['review_frequency'] = 'weekly'
            modified = True
    
    elif para_type == 'resource':
        if 'category' not in post.metadata:
            post.metadata['category'] = ''
            modified = True
        if 'source' not in post.metadata:
            post.metadata['source'] = ''
            modified = True
    
    return modified


def get_para_conventional_name(file_path: Path, post: frontmatter.Post) -> str:
    """Generate PARA-conventional filename."""
    current_name = file_path.name
    para_type = post.metadata.get('para_type', 'inbox')
    
    # Don't rename if already has good PARA naming
    if re.match(r'^\d{4}-\d{2}-\d{2}--', current_name) and para_type == 'daily':
        return current_name
    
    # For daily notes, ensure date prefix
    if para_type == 'daily':
        date_str = post.metadata.get('date_created', datetime.now().strftime('%Y-%m-%d'))
        if isinstance(date_str, str):
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_prefix = date_obj.strftime('%Y-%m-%d')
            except:
                date_prefix = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
        else:
            date_prefix = date_str.strftime('%Y-%m-%d')
        
        # Create slug from existing name or title
        title = post.metadata.get('title', file_path.stem)
        slug = re.sub(r'[^\w\-]', '-', title.lower())
        slug = re.sub(r'-+', '-', slug).strip('-')
        
        return f"{date_prefix}--{slug}.md"
    
    # For other types, use title case
    title = post.metadata.get('title', file_path.stem)
    normalized = re.sub(r'[^\w\s\-]', '', title)
    normalized = ' '.join(word.capitalize() for word in normalized.split())
    normalized = normalized.replace(' ', '_')
    
    return f"{normalized}.md"


def _is_template_file(file_path: Path) -> bool:
    """Check if file is a template."""
    return '01_Templates' in str(file_path) or 'template' in file_path.stem.lower()


def _save_post(file_path: Path, post: frontmatter.Post) -> None:
    """Save frontmatter post to file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(post))
