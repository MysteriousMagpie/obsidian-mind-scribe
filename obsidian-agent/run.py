
"""
CLI entry point for the Obsidian Agent.

Usage:
    python run.py summarize
    python run.py summarize --days 30
"""

import sys
from pathlib import Path

import click

# Add the current directory to Python path so we can import agent modules
sys.path.insert(0, str(Path(__file__).parent))

from agent.config import config
from agent.summarizer import process_observation_notes, generate_weekly_review_markdown
from agent.writer import write_weekly_review, ensure_vault_structure


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


if __name__ == '__main__':
    cli()
