
"""Module for managing wikilinks and updating references when files are moved."""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

from .config import config


def scan_and_update_links(file_moves: Dict[Path, Path], dry_run: bool = False) -> Dict[str, int]:
    """
    Scan vault for wikilinks and update them when files are moved.
    
    Args:
        file_moves: Dictionary mapping old paths to new paths
        dry_run: If True, only report what would be updated
        
    Returns:
        Dictionary with counts of updates performed
    """
    stats = {
        'files_scanned': 0,
        'links_found': 0,
        'links_updated': 0,
        'broken_links': 0
    }
    
    # Create a mapping of old names to new names
    name_mapping = {}
    for old_path, new_path in file_moves.items():
        old_name = old_path.stem
        new_name = new_path.stem
        if old_name != new_name:
            name_mapping[old_name] = new_name
    
    # Scan all markdown files
    for md_file in config.vault_path.rglob("*.md"):
        if md_file.is_file():
            stats['files_scanned'] += 1
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all wikilinks
                wikilink_pattern = r'\[\[([^\]]+)\]\]'
                matches = re.findall(wikilink_pattern, content)
                stats['links_found'] += len(matches)
                
                # Update content if needed
                updated_content = content
                updated = False
                
                for match in matches:
                    link_name = match.split('|')[0].strip()  # Handle display text
                    
                    if link_name in name_mapping:
                        old_link = f"[[{match}]]"
                        new_link_name = name_mapping[link_name]
                        
                        # Preserve display text if it exists
                        if '|' in match:
                            display_text = match.split('|')[1].strip()
                            new_link = f"[[{new_link_name}|{display_text}]]"
                        else:
                            new_link = f"[[{new_link_name}]]"
                        
                        updated_content = updated_content.replace(old_link, new_link)
                        updated = True
                        stats['links_updated'] += 1
                        
                        if dry_run:
                            print(f"  🔗 Would update link in {md_file.name}: {old_link} → {new_link}")
                
                # Save updated content
                if updated and not dry_run:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                
            except Exception as e:
                print(f"❌ Error updating links in {md_file}: {e}")
    
    return stats


def find_broken_links() -> List[Tuple[Path, str]]:
    """
    Find all broken wikilinks in the vault.
    
    Returns:
        List of tuples containing (file_path, broken_link)
    """
    broken_links = []
    
    # Get all markdown files
    all_files = {f.stem for f in config.vault_path.rglob("*.md") if f.is_file()}
    
    # Scan for wikilinks
    for md_file in config.vault_path.rglob("*.md"):
        if md_file.is_file():
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all wikilinks
                wikilink_pattern = r'\[\[([^\]]+)\]\]'
                matches = re.findall(wikilink_pattern, content)
                
                for match in matches:
                    link_name = match.split('|')[0].strip()  # Handle display text
                    
                    if link_name not in all_files:
                        broken_links.append((md_file, link_name))
                        
            except Exception as e:
                print(f"❌ Error scanning {md_file} for broken links: {e}")
    
    return broken_links


def generate_broken_links_report() -> str:
    """
    Generate a markdown report of all broken links.
    
    Returns:
        Markdown formatted report
    """
    broken_links = find_broken_links()
    
    if not broken_links:
        return "# Broken Links Report\n\n✅ No broken links found in the vault!"
    
    report = "# Broken Links Report\n\n"
    report += f"Found {len(broken_links)} broken links:\n\n"
    
    # Group by file
    by_file = {}
    for file_path, link in broken_links:
        if file_path not in by_file:
            by_file[file_path] = []
        by_file[file_path].append(link)
    
    for file_path, links in sorted(by_file.items()):
        rel_path = file_path.relative_to(config.vault_path)
        report += f"## {rel_path}\n\n"
        
        for link in sorted(links):
            report += f"- `[[{link}]]`\n"
        
        report += "\n"
    
    return report
