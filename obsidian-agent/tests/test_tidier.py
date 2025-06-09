
"""Tests for the tidier module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agent.frontmatter_handler import infer_type_from_content, normalize_tags, ensure_frontmatter
import frontmatter


class TestTidier:
    """Test cases for the tidier module."""
    
    def test_infer_type_from_content_observation(self):
        """Test that observation content is correctly identified."""
        content = "I observed that the user behavior changed significantly today."
        note_path = Path("/vault/notes/some-note.md")
        
        result = infer_type_from_content(content, note_path)
        assert result == "observation"
    
    def test_infer_type_from_content_hypothesis(self):
        """Test that hypothesis content is correctly identified."""
        content = "Hypothesis: The new feature will increase user engagement by 20%."
        note_path = Path("/vault/notes/some-note.md")
        
        result = infer_type_from_content(content, note_path)
        assert result == "hypothesis"
    
    def test_infer_type_from_content_review(self):
        """Test that review content is correctly identified."""
        content = "Weekly review of progress and achievements this week."
        note_path = Path("/vault/notes/some-note.md")
        
        result = infer_type_from_content(content, note_path)
        assert result == "review"
    
    def test_infer_type_from_folder_path(self):
        """Test that type is inferred from folder structure."""
        content = "Some generic content here."
        note_path = Path("/vault/3-Areas/Mind-Body-System/observations/note.md")
        
        result = infer_type_from_content(content, note_path)
        assert result == "observation"
    
    def test_infer_type_from_filename(self):
        """Test that type is inferred from filename."""
        content = "Some generic content here."
        note_path = Path("/vault/notes/observation-daily.md")
        
        result = infer_type_from_content(content, note_path)
        assert result == "observation"
    
    def test_infer_type_fallback(self):
        """Test that fallback type is returned for generic content."""
        content = "Just some random thoughts and notes."
        note_path = Path("/vault/notes/random.md")
        
        result = infer_type_from_content(content, note_path)
        assert result == "note"
    
    def test_normalize_tags_from_content(self):
        """Test that hashtags in content are extracted to frontmatter."""
        post = frontmatter.Post("This is content with #productivity and #learning tags.")
        post.metadata = {'tags': []}

        result = normalize_tags(post)

        assert result is True
        assert set(post.metadata['tags']) == {'productivity', 'learning'}

    def test_normalize_tags_hyphenated(self):
        """Tags with hyphens are correctly extracted."""
        post = frontmatter.Post("Content with #my-tag and #another-tag.")
        post.metadata = {'tags': []}

        result = normalize_tags(post)

        assert result is True
        assert set(post.metadata['tags']) == {'my-tag', 'another-tag'}
    
    def test_normalize_tags_merge_existing(self):
        """Test that existing frontmatter tags are merged with content tags."""
        post = frontmatter.Post("Content with #newTag here.")
        post.metadata = {'tags': ['existingTag']}
        
        result = normalize_tags(post)
        
        assert result is True
        assert set(post.metadata['tags']) == {'existingTag', 'newTag'}
    
    def test_normalize_tags_no_changes(self):
        """Test that no changes are made when tags are already normalized."""
        post = frontmatter.Post("Content without hashtags.")
        post.metadata = {'tags': ['existing']}
        
        result = normalize_tags(post)
        
        assert result is False
        assert post.metadata['tags'] == ['existing']
    
    def test_ensure_frontmatter_adds_missing_fields(self):
        """Test that missing frontmatter fields are added."""
        post = frontmatter.Post("Some content")
        post.metadata = {}
        note_path = Path("/vault/observations/test.md")
        
        result = ensure_frontmatter(post, note_path)
        
        assert result is True
        assert 'type' in post.metadata
        assert 'status' in post.metadata
        assert 'tags' in post.metadata
        assert post.metadata['status'] == 'active'
    
    def test_ensure_frontmatter_preserves_existing(self):
        """Test that existing frontmatter is preserved."""
        post = frontmatter.Post("Some content")
        post.metadata = {
            'type': 'custom',
            'status': 'completed',
            'tags': ['existing']
        }
        note_path = Path("/vault/notes/test.md")
        
        result = ensure_frontmatter(post, note_path)
        
        assert result is False  # No changes needed
        assert post.metadata['type'] == 'custom'
        assert post.metadata['status'] == 'completed'
        assert post.metadata['tags'] == ['existing']
