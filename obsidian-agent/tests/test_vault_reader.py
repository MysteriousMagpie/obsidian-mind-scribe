
"""Tests for vault_reader module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from agent.vault_reader import get_observation_notes, read_note_content


class TestVaultReader:
    """Test cases for vault reader functionality."""
    
    @patch('agent.vault_reader.config')
    def test_get_observation_notes_returns_list(self, mock_config):
        """Test that get_observation_notes returns a list."""
        # Mock the vault path
        mock_vault_path = MagicMock()
        mock_config.vault_path = mock_vault_path
        
        # Mock the observations path
        mock_obs_path = MagicMock()
        mock_vault_path.__truediv__.return_value = mock_obs_path
        mock_obs_path.exists.return_value = True
        
        # Mock rglob to return empty list
        mock_obs_path.rglob.return_value = []
        
        result = get_observation_notes(days=7)
        assert isinstance(result, list)
    
    @patch('agent.vault_reader.config')
    def test_get_observation_notes_filters_by_date(self, mock_config):
        """Test that get_observation_notes filters files by modification date."""
        # Mock the vault path structure
        mock_vault_path = MagicMock()
        mock_config.vault_path = mock_vault_path
        
        mock_obs_path = MagicMock()
        mock_vault_path.__truediv__.return_value = mock_obs_path
        mock_obs_path.exists.return_value = True
        
        # Create mock files with different modification times
        now = datetime.now()
        old_file = MagicMock()
        old_file.is_file.return_value = True
        old_file.stat.return_value.st_mtime = (now - timedelta(days=10)).timestamp()
        
        recent_file = MagicMock()
        recent_file.is_file.return_value = True
        recent_file.stat.return_value.st_mtime = (now - timedelta(days=2)).timestamp()
        
        mock_obs_path.rglob.return_value = [old_file, recent_file]
        
        result = get_observation_notes(days=7)
        
        # Should only return the recent file
        assert len(result) == 1
        assert result[0] == recent_file
    
    def test_read_note_content_basic(self):
        """Test reading note content from a file."""
        # This is a simple smoke test
        # In a real scenario, you'd create a temporary file for testing
        content = "# Test Note\n\nThis is a test."
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = content
            
            result = read_note_content(Path("test.md"))
            assert result == content
