
"""Tests for the PARA migrator module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agent.para_migrator import infer_para_type, get_para_folder, update_para_frontmatter
import frontmatter


class TestParaMigrator:
    """Test cases for the PARA migrator module."""
    
    def test_infer_para_type_daily_from_filename(self):
        """Test that daily notes are identified by date filename."""
        content = "Today was a good day."
        note_path = Path("/vault/notes/2024-01-15--daily-note.md")
        
        result = infer_para_type(content, note_path)
        assert result == "daily"
    
    def test_infer_para_type_project_from_content(self):
        """Test that project notes are identified by content keywords."""
        content = "Project: Build new website. Deadline: 2024-02-01. Deliverable: Landing page."
        note_path = Path("/vault/notes/website-project.md")
        
        result = infer_para_type(content, note_path)
        assert result == "project"
    
    def test_infer_para_type_resource_from_filename(self):
        """Test that resource notes are identified by filename."""
        content = "This is a guide on how to use Git effectively."
        note_path = Path("/vault/notes/git-guide.md")
        
        result = infer_para_type(content, note_path)
        assert result == "resource"
    
    def test_infer_para_type_area_from_path(self):
        """Test that area notes are identified by folder path."""
        content = "Personal development goals and responsibilities."
        note_path = Path("/vault/personal/development-goals.md")
        
        result = infer_para_type(content, note_path)
        assert result == "area"
    
    def test_infer_para_type_from_legacy_school_path(self):
        """Test that school notes are categorized as areas."""
        content = "Lecture notes from Computer Science class."
        note_path = Path("/vault/school/2024/spring/cs101/lecture-1.md")
        
        result = infer_para_type(content, note_path)
        assert result == "area"
    
    def test_infer_para_type_fallback_to_inbox(self):
        """Test that unclassified notes default to inbox."""
        content = "Random thoughts and ideas."
        note_path = Path("/vault/notes/random-thoughts.md")
        
        result = infer_para_type(content, note_path)
        assert result == "inbox"
    
    @patch('agent.para_migrator.config')
    def test_get_para_folder_project(self, mock_config):
        """Test that project notes go to projects folder."""
        mock_config.vault_path = Path("/vault")
        
        post = frontmatter.Post("Project content")
        post.metadata = {'para_type': 'project'}
        note_path = Path("/vault/notes/test.md")
        
        result = get_para_folder('project', note_path, post)
        assert result == Path("/vault/02_Projects")
    
    @patch('agent.para_migrator.config')
    def test_get_para_folder_area_personal(self, mock_config):
        """Test that personal area notes go to personal subfolder."""
        mock_config.vault_path = Path("/vault")
        
        post = frontmatter.Post("Personal content")
        post.metadata = {'para_type': 'area'}
        note_path = Path("/vault/personal/test.md")
        
        result = get_para_folder('area', note_path, post)
        assert result == Path("/vault/03_Areas/Personal")
    
    @patch('agent.para_migrator.config')
    def test_get_para_folder_resource_guides(self, mock_config):
        """Test that guide resources go to guides subfolder."""
        mock_config.vault_path = Path("/vault")
        
        post = frontmatter.Post("Guide content with tutorial information")
        post.metadata = {'para_type': 'resource'}
        note_path = Path("/vault/guides/test.md")
        
        result = get_para_folder('resource', note_path, post)
        assert result == Path("/vault/04_Resources/Guides")
    
    def test_update_para_frontmatter_adds_required_fields(self):
        """Test that required PARA frontmatter fields are added."""
        post = frontmatter.Post("Some content")
        post.metadata = {}
        note_path = Path("/vault/test.md")
        
        result = update_para_frontmatter(post, note_path)
        
        assert result is True
        assert 'para_type' in post.metadata
        assert 'status' in post.metadata
        assert 'tags' in post.metadata
        assert 'last_modified' in post.metadata
        assert post.metadata['status'] == 'active'
    
    def test_update_para_frontmatter_adds_project_fields(self):
        """Test that project-specific frontmatter fields are added."""
        post = frontmatter.Post("Project content")
        post.metadata = {'para_type': 'project'}
        note_path = Path("/vault/test.md")
        
        result = update_para_frontmatter(post, note_path)
        
        assert result is True
        assert 'priority' in post.metadata
        assert 'deadline' in post.metadata
        assert post.metadata['priority'] == 'medium'
    
    def test_update_para_frontmatter_adds_area_fields(self):
        """Test that area-specific frontmatter fields are added."""
        post = frontmatter.Post("Area content")
        post.metadata = {'para_type': 'area'}
        note_path = Path("/vault/test.md")
        
        result = update_para_frontmatter(post, note_path)
        
        assert result is True
        assert 'last_reviewed' in post.metadata
        assert 'review_frequency' in post.metadata
        assert post.metadata['review_frequency'] == 'weekly'
    
    def test_update_para_frontmatter_preserves_existing(self):
        """Test that existing frontmatter is preserved."""
        post = frontmatter.Post("Content")
        post.metadata = {
            'para_type': 'project',
            'status': 'completed',
            'priority': 'high',
            'deadline': '2024-12-31',
            'tags': ['existing'],
            'last_modified': '2024-01-01'
        }
        note_path = Path("/vault/test.md")
        
        result = update_para_frontmatter(post, note_path)
        
        assert result is False  # No changes needed
        assert post.metadata['status'] == 'completed'
        assert post.metadata['priority'] == 'high'
        assert post.metadata['deadline'] == '2024-12-31'
