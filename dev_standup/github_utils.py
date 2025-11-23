"""
GitHub repository utilities for cloning and managing repos.
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Optional
import re


def is_github_url(url: str) -> bool:
    """Check if the given string is a GitHub URL."""
    github_patterns = [
        r'^https?://github\.com/[\w-]+/[\w.-]+',
        r'^git@github\.com:[\w-]+/[\w.-]+\.git$',
        r'^github\.com/[\w-]+/[\w.-]+',
    ]
    return any(re.match(pattern, url) for pattern in github_patterns)


def normalize_github_url(url: str) -> str:
    """Normalize GitHub URL to HTTPS format."""
    # Remove .git suffix
    url = url.rstrip('.git')
    
    # Convert SSH to HTTPS
    if url.startswith('git@github.com:'):
        url = url.replace('git@github.com:', 'https://github.com/')
    
    # Add https:// if missing
    if url.startswith('github.com/'):
        url = 'https://' + url
    
    return url + '.git'


def clone_repository(repo_url: str, target_dir: Optional[Path] = None) -> Path:
    """
    Clone a GitHub repository.
    
    Args:
        repo_url: GitHub repository URL
        target_dir: Optional target directory. If None, creates temp directory.
        
    Returns:
        Path to the cloned repository
        
    Raises:
        Exception: If git clone fails
    """
    if target_dir is None:
        # Create temp directory
        temp_base = Path(tempfile.gettempdir()) / 'dev-standup-repos'
        temp_base.mkdir(exist_ok=True)
        
        # Extract repo name from URL
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        target_dir = temp_base / repo_name
        
        # Remove if already exists
        if target_dir.exists():
            import shutil
            shutil.rmtree(target_dir)
    
    # Clone the repository
    try:
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', repo_url, str(target_dir)],
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )
        return target_dir
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        raise Exception(f"Git clone failed: {error_msg}")
    except subprocess.TimeoutExpired:
        raise Exception("Git clone timed out after 120 seconds")
