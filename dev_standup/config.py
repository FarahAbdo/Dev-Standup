"""
Configuration management for dev-standup.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(".env")
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Application configuration."""
    
    # LLM Provider
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # Default Settings
    DEFAULT_MOOD = os.getenv("DEFAULT_MOOD", "neutral")
    DEFAULT_HOURS = int(os.getenv("DEFAULT_HOURS", "24"))
    
    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate configuration and return list of errors.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append(
                "OpenAI API key not found. Set OPENAI_API_KEY in .env file "
                "or switch to Ollama by setting LLM_PROVIDER=ollama"
            )
        
        if cls.LLM_PROVIDER not in ["openai", "ollama"]:
            errors.append(
                f"Invalid LLM_PROVIDER: {cls.LLM_PROVIDER}. "
                "Must be 'openai' or 'ollama'"
            )
        
        return errors
