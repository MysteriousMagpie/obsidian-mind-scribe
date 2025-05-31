
"""Configuration management for the Obsidian agent."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the Obsidian agent."""
    
    def __init__(self):
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.vault_path: Path = Path(
            os.getenv("VAULT_PATH", "~/Obsidian/Personal-System")
        ).expanduser()
        
    def validate(self) -> None:
        """Validate that required configuration is present."""
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        
        if not self.vault_path.exists():
            raise ValueError(
                f"Vault path does not exist: {self.vault_path}. "
                "Please check your VAULT_PATH configuration."
            )


# Global config instance
config = Config()
