"""
LLM integration for commit summarization.
"""

from abc import ABC, abstractmethod
from typing import List
import json

from dev_standup.config import Config
from dev_standup.prompts import get_prompts
from dev_standup.git_scanner import CommitInfo, format_commits_for_llm


class BaseSummarizer(ABC):
    """Base class for LLM summarizers."""
    
    def __init__(self, mood: str = "neutral"):
        """
        Initialize the summarizer.
        
        Args:
            mood: Mood for the summary ("neutral", "roast", or "hero")
        """
        self.mood = mood
        self.system_prompt, self.user_template = get_prompts(mood)
    
    @abstractmethod
    def summarize(self, commits: List[CommitInfo]) -> str:
        """
        Summarize commits using the LLM.
        
        Args:
            commits: List of commit information
            
        Returns:
            Summarized text
        """
        pass
    
    def _format_prompt(self, commits: List[CommitInfo]) -> str:
        """Format commits into the user prompt."""
        commits_text = format_commits_for_llm(commits)
        return self.user_template.format(commits=commits_text)


class OpenAISummarizer(BaseSummarizer):
    """Summarizer using OpenAI API."""
    
    def __init__(self, mood: str = "neutral"):
        super().__init__(mood)
        
        from openai import OpenAI
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
    
    def summarize(self, commits: List[CommitInfo]) -> str:
        """Summarize commits using OpenAI."""
        if not commits:
            return "No commits to summarize."
        
        user_prompt = self._format_prompt(commits)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Error generating summary: {e}"


class OllamaSummarizer(BaseSummarizer):
    """Summarizer using local Ollama."""
    
    def __init__(self, mood: str = "neutral"):
        super().__init__(mood)
        
        import requests
        self.requests = requests
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
    
    def summarize(self, commits: List[CommitInfo]) -> str:
        """Summarize commits using Ollama."""
        if not commits:
            return "No commits to summarize."
        
        user_prompt = self._format_prompt(commits)
        
        try:
            # Combine system and user prompts for Ollama
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 500
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return f"Error: Ollama returned status {response.status_code}"
        
        except self.requests.exceptions.ConnectionError:
            return (
                "Error: Cannot connect to Ollama. "
                "Make sure Ollama is running (http://localhost:11434) "
                "or switch to OpenAI by setting LLM_PROVIDER=openai in .env"
            )
        except Exception as e:
            return f"Error generating summary: {e}"


def create_summarizer(mood: str = "neutral") -> BaseSummarizer:
    """
    Create a summarizer based on the configured LLM provider.
    
    Args:
        mood: Mood for the summary
        
    Returns:
        Appropriate summarizer instance
    """
    provider = Config.LLM_PROVIDER
    
    if provider == "openai":
        return OpenAISummarizer(mood)
    elif provider == "ollama":
        return OllamaSummarizer(mood)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
