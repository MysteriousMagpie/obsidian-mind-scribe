
"""Tests for GPT client module."""

import pytest
from unittest.mock import patch, MagicMock

from agent.gpt_client import GPTClient


class TestGPTClient:
    """Test cases for GPT client functionality."""
    
    @patch('agent.gpt_client.openai')
    def test_summarize_returns_dict_with_required_keys(self, mock_openai):
        """Test that summarize returns a dict with the required keys."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """
        SUMMARY: This is a test summary
        HYPOTHESIS: This is a test hypothesis
        FOLLOW_UP: This is a test follow-up question
        """
        mock_openai.chat.completions.create.return_value = mock_response
        
        client = GPTClient()
        result = client.summarize("Test observation note")
        
        # Check that all required keys are present
        assert isinstance(result, dict)
        assert "summary" in result
        assert "hypothesis" in result
        assert "follow_up_question" in result
        
        # Check that values are strings
        assert isinstance(result["summary"], str)
        assert isinstance(result["hypothesis"], str)
        assert isinstance(result["follow_up_question"], str)
    
    def test_parse_response_basic(self):
        """Test parsing of GPT response content."""
        client = GPTClient()
        
        content = """
        SUMMARY: Test summary content
        HYPOTHESIS: Test hypothesis content
        FOLLOW_UP: Test follow-up content
        """
        
        result = client._parse_response(content)
        
        assert result["summary"] == "Test summary content"
        assert result["hypothesis"] == "Test hypothesis content"
        assert result["follow_up_question"] == "Test follow-up content"
    
    def test_parse_response_multiline(self):
        """Test parsing of multiline GPT response."""
        client = GPTClient()
        
        content = """
        SUMMARY: This is a longer summary
        that spans multiple lines
        HYPOTHESIS: This hypothesis also
        spans multiple lines
        FOLLOW_UP: What about this question?
        """
        
        result = client._parse_response(content)
        
        assert "longer summary that spans multiple lines" in result["summary"]
        assert "hypothesis also spans multiple lines" in result["hypothesis"]
        assert "What about this question?" in result["follow_up_question"]
