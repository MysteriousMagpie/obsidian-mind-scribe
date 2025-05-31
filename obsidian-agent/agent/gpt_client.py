
"""OpenAI GPT client for summarizing observation notes."""

from typing import Dict, Any
import openai
from .config import config


class GPTClient:
    """Client for interacting with OpenAI's GPT models."""
    
    def __init__(self):
        """Initialize the GPT client with API key."""
        openai.api_key = config.openai_api_key
    
    def summarize(self, text: str) -> Dict[str, str]:
        """
        Summarize observation text using GPT-4.
        
        Args:
            text: The observation note content to summarize
            
        Returns:
            Dictionary with keys: summary, hypothesis, follow_up_question
        """
        prompt = f"""
        Please analyze the following observation note and provide:
        1. A concise summary of the key observations
        2. A hypothesis about patterns or insights
        3. A follow-up question for deeper investigation

        Observation note:
        {text}

        Please format your response as:
        SUMMARY: [your summary here]
        HYPOTHESIS: [your hypothesis here]
        FOLLOW_UP: [your follow-up question here]
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing personal observation notes and identifying patterns, insights, and areas for further exploration."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return self._parse_response(content)
            
        except Exception as e:
            raise RuntimeError(f"Failed to get GPT response: {str(e)}")
    
    def _parse_response(self, content: str) -> Dict[str, str]:
        """
        Parse the structured GPT response into a dictionary.
        
        Args:
            content: The raw GPT response content
            
        Returns:
            Dictionary with parsed summary, hypothesis, and follow_up_question
        """
        result = {
            "summary": "",
            "hypothesis": "",
            "follow_up_question": ""
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("SUMMARY:"):
                current_section = "summary"
                result["summary"] = line.replace("SUMMARY:", "").strip()
            elif line.startswith("HYPOTHESIS:"):
                current_section = "hypothesis"
                result["hypothesis"] = line.replace("HYPOTHESIS:", "").strip()
            elif line.startswith("FOLLOW_UP:"):
                current_section = "follow_up_question"
                result["follow_up_question"] = line.replace("FOLLOW_UP:", "").strip()
            elif current_section and line:
                # Continue adding to the current section if we have content
                result[current_section] += " " + line
        
        return result


# Global GPT client instance
gpt_client = GPTClient()
