"""
Git repository scanning and commit extraction.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

import git
from git import Repo, Commit


@dataclass
class CommitInfo:
    """Information about a single commit."""
    sha: str
    message: str
    author: str
    timestamp: datetime
    files_changed: List[str]
    repo_name: str


class GitScanner:
    """Scans git repositories for recent commits."""
    
    def __init__(self, hours: int = 24, all_authors: bool = False):
        """
        Initialize the scanner.
        
        Args:
            hours: Number of hours to look back for commits
            all_authors: If True, include commits from all authors. If False, only current user.
        """
        self.hours = hours
        self.all_authors = all_authors
        self.cutoff_time = datetime.now() - timedelta(hours=hours)
    
    def scan_repository(self, repo_path: Path) -> List[CommitInfo]:
        """
        Scan a single repository for recent commits.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            List of CommitInfo objects for commits within the time range
        """
        try:
            repo = Repo(repo_path)
            
            if repo.bare:
                return []
            
            commits = []
            repo_name = repo_path.name
            
            # Get current user's git email
            user_email = None
            if not self.all_authors:
                try:
                    git_config = repo.config_reader()
                    user_email = git_config.get_value("user", "email")
                except Exception:
                    # If can't get email, include all commits
                    user_email = None
            
            # Iterate through commits in all branches
            for commit in repo.iter_commits(all=True, max_count=200):
                commit_time = datetime.fromtimestamp(commit.committed_date)
                
                # Skip commits outside time range
                if commit_time < self.cutoff_time:
                    continue
                
                # Filter by current user if we have their email and not showing all authors
                if not self.all_authors and user_email and commit.author.email != user_email:
                    continue
                
                # Get list of changed files
                try:
                    files_changed = list(commit.stats.files.keys())
                except Exception:
                    files_changed = []
                
                commits.append(CommitInfo(
                    sha=commit.hexsha[:8],
                    message=commit.message.strip(),
                    author=commit.author.name,
                    timestamp=commit_time,
                    files_changed=files_changed,
                    repo_name=repo_name
                ))
            
            # Sort by timestamp, most recent first
            commits.sort(key=lambda c: c.timestamp, reverse=True)
            return commits
            
        except git.InvalidGitRepositoryError:
            return []
        except Exception as e:
            print(f"Warning: Error scanning {repo_path}: {e}")
            return []
    
    def find_repositories(self, root_path: Path, max_depth: int = 3) -> List[Path]:
        """
        Find all git repositories under the given path.
        
        Args:
            root_path: Root directory to search
            max_depth: Maximum depth to search
            
        Returns:
            List of paths to git repositories
        """
        repos = []
        
        def search_dir(path: Path, depth: int):
            if depth > max_depth:
                return
            
            # Check if this directory is a git repo
            if (path / ".git").exists():
                repos.append(path)
                return  # Don't search inside git repos
            
            # Search subdirectories
            try:
                for item in path.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        search_dir(item, depth + 1)
            except PermissionError:
                pass
        
        search_dir(root_path, 0)
        return repos
    
    def scan_multiple_repositories(
        self, 
        repo_paths: Optional[List[Path]] = None,
        search_root: Optional[Path] = None
    ) -> Dict[str, List[CommitInfo]]:
        """
        Scan multiple repositories.
        
        Args:
            repo_paths: Explicit list of repository paths
            search_root: Root path to search for repositories
            
        Returns:
            Dictionary mapping repository names to lists of commits
        """
        if repo_paths is None and search_root is not None:
            repo_paths = self.find_repositories(search_root)
        elif repo_paths is None:
            repo_paths = []
        
        results = {}
        
        for repo_path in repo_paths:
            commits = self.scan_repository(repo_path)
            if commits:  # Only include repos with commits
                results[repo_path.name] = commits
        
        return results


def format_commits_for_llm(commits: List[CommitInfo]) -> str:
    """
    Format commits into a text representation for LLM input.
    
    Args:
        commits: List of CommitInfo objects
        
    Returns:
        Formatted string representation
    """
    if not commits:
        return "No commits found."
    
    lines = []
    for commit in commits:
        time_str = commit.timestamp.strftime("%Y-%m-%d %H:%M")
        lines.append(f"[{time_str}] {commit.message}")
        if commit.files_changed:
            # Show up to 3 files
            files_preview = commit.files_changed[:3]
            if len(commit.files_changed) > 3:
                files_preview.append(f"... and {len(commit.files_changed) - 3} more")
            lines.append(f"  Files: {', '.join(files_preview)}")
    
    return "\n".join(lines)
