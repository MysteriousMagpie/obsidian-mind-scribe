
"""
CLI entry point for the Obsidian Agent.

Usage:
    python run.py summarize
    python run.py summarize --days 30
    python run.py tidy
    python run.py tidy --dry-run
    python run.py migrate-para
    python run.py migrate-para --dry-run
    python run.py create-templates
    python run.py fix-links
    python run.py backup-vault
"""

import sys
from pathlib import Path

import click

# Add the current directory to Python path so we can import agent modules
sys.path.insert(0, str(Path(__file__).parent))

from agent.config import config
from agent.summarizer import process_observation_notes, generate_weekly_review_markdown
from agent.writer import write_weekly_review, ensure_vault_structure
from agent.tidier import tidy_vault
from agent.para_migrator import migrate_to_para
from agent.templates import create_templates
from agent.link_manager import generate_broken_links_report


@click.group()
def cli():
    """Obsidian Agent - Summarize observation notes and generate weekly reviews."""
    pass


@cli.command()
@click.option(
    '--days', 
    default=7, 
    help='Number of days to look back for observation notes (default: 7)',
    type=int
)
@click.option(
    '--output-date',
    help='Date string for output file (default: today)',
    type=str
)
def summarize(days: int, output_date: str):
    """Generate a weekly review from recent observation notes."""
    
    try:
        # Validate configuration
        config.validate()
        
        print(f"🔍 Scanning for observation notes from the last {days} days...")
        print(f"📁 Vault path: {config.vault_path}")
        
        # Ensure vault structure exists
        ensure_vault_structure()
        
        # Process observation notes
        processed_data = process_observation_notes(days)
        
        print(f"📝 Found {processed_data['notes_processed']} notes to process")
        print(f"📅 Date range: {processed_data['date_range']}")
        
        if processed_data['notes_processed'] == 0:
            print("⚠️  No observation notes found in the specified time period.")
            print(f"   Check that notes exist in: {config.vault_path}/3-Areas/Mind-Body-System/observations/")
            return
        
        # Generate markdown content
        print("🤖 Generating weekly review with GPT-4...")
        markdown_content = generate_weekly_review_markdown(processed_data)
        
        # Write the review file
        review_file = write_weekly_review(markdown_content, output_date)
        
        print(f"✅ Weekly review complete!")
        print(f"📄 Review saved to: {review_file}")
        
        # Show a preview of the content
        lines = markdown_content.split('\n')
        preview_lines = lines[:10]
        print("\n📖 Preview:")
        print("=" * 50)
        for line in preview_lines:
            print(line)
        if len(lines) > 10:
            print("...")
        print("=" * 50)
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be done without making changes'
)
def tidy(dry_run: bool):
    """Tidy and organize markdown files in the Obsidian vault."""
    
    try:
        # Validate configuration
        config.validate()
        
        print(f"🧹 Tidying Obsidian vault...")
        print(f"📁 Vault path: {config.vault_path}")
        
        # Run tidying process
        stats = tidy_vault(dry_run=dry_run)
        
        # Print summary
        print("\n📊 Tidying Summary:")
        print("=" * 40)
        print(f"Files processed: {stats['files_processed']}")
        print(f"Frontmatter added: {stats['frontmatter_added']}")
        print(f"Files moved: {stats['files_moved']}")
        print(f"Files renamed: {stats['files_renamed']}")
        print(f"Tags normalized: {stats['tags_normalized']}")
        
        if stats['errors'] > 0:
            print(f"Errors encountered: {stats['errors']}")
        
        if dry_run:
            print("\n🧪 This was a dry run - no files were modified.")
            print("   Run without --dry-run to apply changes.")
        else:
            print(f"\n✅ Tidying complete!")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be done without making changes'
)
def migrate_para(dry_run: bool):
    """Migrate vault to PARA methodology structure."""
    
    try:
        # Validate configuration
        config.validate()
        
        print(f"🚀 Migrating vault to PARA methodology...")
        print(f"📁 Vault path: {config.vault_path}")
        
        if not dry_run:
            confirm = click.confirm(
                "⚠️  This will restructure your entire vault. Continue?", 
                default=False
            )
            if not confirm:
                print("Migration cancelled.")
                return
        
        # Run PARA migration
        stats = migrate_to_para(dry_run=dry_run)
        
        # Print summary
        print("\n📊 PARA Migration Summary:")
        print("=" * 50)
        print(f"Files processed: {stats['files_processed']}")
        print(f"Folders created: {stats['folders_created']}")
        print(f"Files moved: {stats['files_moved']}")
        print(f"Files renamed: {stats['files_renamed']}")
        print(f"Frontmatter updated: {stats['frontmatter_updated']}")
        print(f"Templates created: {stats['templates_created']}")
        print(f"Links updated: {stats['links_updated']}")
        
        if stats['errors'] > 0:
            print(f"Errors encountered: {stats['errors']}")
        
        if dry_run:
            print("\n🧪 This was a dry run - no files were modified.")
            print("   Run without --dry-run to apply changes.")
        else:
            print(f"\n✅ PARA migration complete!")
            print("📖 Check the 01_Templates folder for new templates.")
            print("🔗 Run 'fix-links' if you notice any broken wikilinks.")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


@cli.command()
def create_templates():
    """Create PARA methodology templates in the vault."""
    
    try:
        # Validate configuration
        config.validate()
        
        print(f"📝 Creating PARA templates...")
        print(f"📁 Vault path: {config.vault_path}")
        
        # Create templates
        templates = create_templates()
        
        print(f"\n✅ Created {len(templates)} templates:")
        for name, path in templates.items():
            rel_path = path.relative_to(config.vault_path)
            print(f"  📄 {rel_path}")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


@cli.command()
def fix_links():
    """Generate a report of broken wikilinks in the vault."""
    
    try:
        # Validate configuration
        config.validate()
        
        print(f"🔗 Scanning vault for broken wikilinks...")
        print(f"📁 Vault path: {config.vault_path}")
        
        # Generate broken links report
        report = generate_broken_links_report()
        
        # Save report to vault
        report_path = config.vault_path / "broken-links-report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Report saved to: {report_path}")
        
        # Show preview
        lines = report.split('\n')
        preview_lines = lines[:20]
        print("\n📖 Preview:")
        print("=" * 50)
        for line in preview_lines:
            print(line)
        if len(lines) > 20:
            print("...")
        print("=" * 50)
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


@cli.command()
def backup_vault():
    """Create a backup of the vault before major operations."""
    
    try:
        # Validate configuration
        config.validate()
        
        print(f"💾 Creating vault backup...")
        print(f"📁 Vault path: {config.vault_path}")
        
        from datetime import datetime
        import shutil
        
        # Create backup directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"vault_backup_{timestamp}"
        backup_path = config.vault_path.parent / backup_name
        
        # Copy vault
        shutil.copytree(config.vault_path, backup_path)
        
        print(f"✅ Backup created: {backup_path}")
        print(f"💡 Use this backup to restore if needed.")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
