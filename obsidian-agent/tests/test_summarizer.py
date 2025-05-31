
"""Tests for summarizer module."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from agent.summarizer import process_observation_notes, generate_weekly_review_markdown


class TestSummarizer:
    """Test cases for summarizer functionality."""
    
    @patch('agent.summarizer.get_observation_notes')
    def test_process_observation_notes_empty_list(self, mock_get_notes):
        """Test processing when no notes are found."""
        mock_get_notes.return_value = []
        
        result = process_observation_notes(days=7)
        
        assert result["notes_processed"] == 0
        assert result["summaries"] == []
        assert "last 7 days" in result["period"]
    
    @patch('agent.summarizer.gpt_client')
    @patch('agent.summarizer.read_note_content')
    @patch('agent.summarizer.get_observation_notes')
    def test_process_observation_notes_with_files(self, mock_get_notes, mock_read_content, mock_gpt):
        """Test processing when notes are found."""
        # Mock file objects
        mock_file = MagicMock()
        mock_file.name = "test-note.md"
        mock_file.stat.return_value.st_mtime = 1640995200  # Fixed timestamp
        mock_get_notes.return_value = [mock_file]
        
        # Mock file content
        mock_read_content.return_value = "# Test Note\n\nThis is test content."
        
        # Mock GPT response
        mock_gpt.summarize.return_value = {
            "summary": "Test summary",
            "hypothesis": "Test hypothesis",
            "follow_up_question": "Test question"
        }
        
        result = process_observation_notes(days=7)
        
        assert result["notes_processed"] == 1
        assert len(result["summaries"]) == 1
        assert result["summaries"][0]["file_name"] == "test-note.md"
        assert result["summaries"][0]["analysis"]["summary"] == "Test summary"
    
    def test_generate_weekly_review_markdown_structure(self):
        """Test that generated markdown has the expected structure."""
        processed_data = {
            "notes_processed": 2,
            "summaries": [
                {
                    "file_name": "note1.md",
                    "analysis": {
                        "summary": "Summary 1",
                        "hypothesis": "Hypothesis 1",
                        "follow_up_question": "Question 1"
                    },
                    "word_count": 50
                },
                {
                    "file_name": "note2.md",
                    "analysis": {
                        "summary": "Summary 2",
                        "hypothesis": "Hypothesis 2",
                        "follow_up_question": "Question 2"
                    },
                    "word_count": 75
                }
            ],
            "period": "last 7 days",
            "date_range": "2024-01-01 to 2024-01-07"
        }
        
        markdown = generate_weekly_review_markdown(processed_data)
        
        # Check for expected sections
        assert "# Weekly Review" in markdown
        assert "## Overview" in markdown
        assert "## Individual Note Summaries" in markdown
        assert "## Overall Insights" in markdown
        assert "### Key Themes" in markdown
        assert "### Research Questions" in markdown
        assert "### Next Steps" in markdown
        
        # Check that note content is included
        assert "note1.md" in markdown
        assert "note2.md" in markdown
        assert "Summary 1" in markdown
        assert "Summary 2" in markdown
