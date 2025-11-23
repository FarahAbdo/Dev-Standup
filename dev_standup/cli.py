"""
CLI interface for dev-standup with GitHub URL support.
"""

import sys
from pathlib import Path
from typing import Optional
import tempfile
import shutil
import time

import click
from colorama import init, Fore, Style, Back

from dev_standup.config import Config
from dev_standup.git_scanner import GitScanner
from dev_standup.summarizer import create_summarizer
from dev_standup.github_utils import is_github_url, normalize_github_url, clone_repository

# Initialize colorama for Windows support
init()

# ASCII Art Banner
BANNER = f"""{Fore.CYAN}{Style.BRIGHT}
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║  ██████╗ ███████╗██╗   ██╗      ███████╗████████╗ █████╗ ███╗   ██╗   ║
║  ██╔══██╗██╔════╝██║   ██║      ██╔════╝╚══██╔══╝██╔══██╗████╗  ██║   ║
║  ██║  ██║█████╗  ██║   ██║█████╗███████╗   ██║   ███████║██╔██╗ ██║   ║
║  ██║  ██║██╔══╝  ╚██╗ ██╔╝╚════╝╚════██║   ██║   ██╔══██║██║╚██╗██║   ║
║  ██████╔╝███████╗ ╚████╔╝       ███████║   ██║   ██║  ██║██║ ╚████║   ║
║  ╚═════╝ ╚══════╝  ╚═══╝        ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝   ║
║                                                                       ║
║                 AI-Powered Standup Summary Generator                  ║
║                    Never forget yesterday again                       ║
╚═══════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""


def print_banner():
    """Print the ASCII art banner."""
    print(BANNER)


def print_header(text: str, color: str = Fore.CYAN):
    """Print a colored header with box."""
    width = 71
    print(f"\n{color}{Style.BRIGHT}╔{'═' * width}╗")
    padding = (width - len(text) - 2) // 2
    print(f"║{' ' * padding} {text} {' ' * (width - len(text) - padding - 2)}║")
    print(f"╚{'═' * width}╝{Style.RESET_ALL}")


def print_box(text: str, color: str = Fore.WHITE):
    """Print text in a box."""
    width = 69
    lines = text.split('\n')
    print(f"{color}┌{'─' * width}┐")
    for line in lines:
        padding = width - len(line)
        print(f"│ {line}{' ' * (padding - 1)}│")
    print(f"└{'─' * width}┘{Style.RESET_ALL}")


def print_success(text: str):
    """Print success message."""
    print(f"{Fore.GREEN}{Style.BRIGHT}✔{Style.RESET_ALL} {Fore.GREEN}{text}{Style.RESET_ALL}")


def print_error(text: str):
    """Print error message."""
    print(f"{Fore.RED}{Style.BRIGHT}✖{Style.RESET_ALL} {Fore.RED}{text}{Style.RESET_ALL}", file=sys.stderr)


def print_warning(text: str):
    """Print warning message."""
    print(f"{Fore.YELLOW}{Style.BRIGHT}⚠{Style.RESET_ALL} {Fore.YELLOW}{text}{Style.RESET_ALL}")


def print_info(text: str):
    """Print info message."""
    print(f"{Fore.BLUE}{Style.BRIGHT}ℹ{Style.RESET_ALL} {Fore.BLUE}{text}{Style.RESET_ALL}")


def print_step(step_num: int, total: int, text: str):
    """Print a step indicator."""
    print(f"{Fore.CYAN}{Style.BRIGHT}[{step_num}/{total}]{Style.RESET_ALL} {text}")


def print_spinner(text: str, duration: float = 0.5):
    """Show a simple spinner animation."""
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        print(f'\r{Fore.CYAN}{frame}{Style.RESET_ALL} {text}', end='', flush=True)
        time.sleep(0.1)
        i += 1
    print(f'\r{Fore.GREEN}✔{Style.RESET_ALL} {text}')



@click.command()
@click.option(
    "--mood",
    type=click.Choice(["neutral", "roast", "hero"], case_sensitive=False),
    default=None,
    help="Mood for the summary (neutral, roast, or hero)"
)
@click.option(
    "--hours",
    type=int,
    default=None,
    help="Number of hours to look back (default: 24)"
)
@click.option(
    "--all-repos",
    is_flag=True,
    help="Scan all git repositories in the current directory and subdirectories"
)
@click.option(
    "--repo",
    type=str,
    default=None,
    help="GitHub repository URL or local path to scan"
)
@click.option(
    "--provider",
    type=click.Choice(["openai", "ollama"], case_sensitive=False),
    default=None,
    help="LLM provider to use (overrides .env setting)"
)
@click.option(
    "--all-authors",
    is_flag=True,
    help="Include commits from all authors (default: only your commits)"
)
def main(
    mood: Optional[str],
    hours: Optional[int],
    all_repos: bool,
    repo: Optional[str],
    provider: Optional[str],
    all_authors: bool
):
    """
    Dev-Standup: Generate AI-powered standup summaries from git commits.
    
    By default, scans the current directory's git repository for commits
    from the last 24 hours and generates a summary.
    
    Examples:
    
        dev-standup                                    # Basic usage in current repo
        
        dev-standup --mood roast                       # Sarcastic summary
        
        dev-standup --repo https://github.com/user/repo  # Clone and scan GitHub repo
        
        dev-standup --hours 48 --all-authors          # Last 48 hours, all users
        
        dev-standup --all-repos                        # All repos in workspace
    """
    
    # Show banner
    print_banner()
    
    # Override config with CLI arguments
    if provider:
        Config.LLM_PROVIDER = provider.lower()
    
    if mood is None:
        mood = Config.DEFAULT_MOOD
    
    if hours is None:
        hours = Config.DEFAULT_HOURS
    
    # Validate configuration
    print_step(1, 4, "Validating configuration...")
    errors = Config.validate()
    if errors:
        for error in errors:
            print_error(error)
        sys.exit(1)
    print_success("Configuration valid")
    
    # Handle GitHub URL or local path
    scan_path = None
    cleanup_temp_dir = False
    
    print_step(2, 4, "Preparing repository...")
    
    if repo:
        if is_github_url(repo):
            # Clone GitHub repository
            print_info("Detected GitHub URL - cloning repository...")
            try:
                repo_url = normalize_github_url(repo)
                print_spinner("Cloning repository", 1.0)
                scan_path = clone_repository(repo_url)
                cleanup_temp_dir = True
                print_success(f"Repository cloned successfully")
            except Exception as e:
                print_error(f"Failed to clone repository: {e}")
                sys.exit(1)
        else:
            # Local path
            scan_path = Path(repo)
            if not scan_path.exists():
                print_error(f"Path does not exist: {scan_path}")
                sys.exit(1)
            print_success(f"Local repository found: {scan_path.name}")
    else:
        # Use current directory
        scan_path = Path.cwd()
        print_success(f"Using current directory: {scan_path.name}")
    
    try:
        # Initialize scanner
        print_step(3, 4, "Scanning git commits...")
        scanner = GitScanner(hours=hours, all_authors=all_authors)
        
        # Scan repositories
        if all_repos:
            print_spinner(f"Discovering repositories in {scan_path.name}", 0.5)
            repos_commits = scanner.scan_multiple_repositories(search_root=scan_path)
            
            if not repos_commits:
                print_warning(f"No git repositories with recent commits found")
                print_info("Try: Increase time range with --hours or check git repositories")
                return
            
            print_success(f"Found {len(repos_commits)} repositories with commits!")
        else:
            # Scan single repository
            print_spinner(f"Analyzing commits in {scan_path.name}", 0.5)
            commits = scanner.scan_repository(scan_path)
            
            if not commits:
                print_warning(f"No commits found in the last {hours} hours")
                print("\n" + "─" * 71)
                print_info("Tips:")
                print(f"   • Try: {Fore.CYAN}--hours 48{Style.RESET_ALL} for longer range")
                print(f"   • Try: {Fore.CYAN}--all-authors{Style.RESET_ALL} to include everyone")
                print(f"   • Try: {Fore.CYAN}--all-repos{Style.RESET_ALL} to scan workspace")
                print("─" * 71)
                return
            
            repos_commits = {scan_path.name: commits}
            print_success(f"Found {len(commits)} commits!")
        
        # Initialize summarizer
        print_step(4, 4, "Generating AI summary...")
        
        print_info(f"Provider: {Config.LLM_PROVIDER.upper()} | Mode: {mood.upper()}")
        
        try:
            summarizer = create_summarizer(mood=mood)
            print_success("AI ready!")
        except Exception as e:
            print_error(f"Failed to initialize LLM: {e}")
            sys.exit(1)
        
        # Generate summaries for each repository
        print_header("STANDUP SUMMARY", Fore.MAGENTA)
        
        for repo_name, commits in repos_commits.items():
            if len(repos_commits) > 1:
                print(f"\n{Fore.CYAN}{Style.BRIGHT}┌─ Repository: {repo_name}")
                print(f"└{'─' * 69}{Style.RESET_ALL}")
            
            print_spinner("Processing with AI", 1.0)
            summary = summarizer.summarize(commits)
            
            # Print summary in a box
            print(f"\n{Fore.WHITE}{summary}{Style.RESET_ALL}\n")
        
        # Footer
        print(f"\n{Fore.GREEN}{Style.BRIGHT}{'═' * 71}")
        print(f"{'Ready for standup! Good luck!':^71}")
        print(f"{'═' * 71}{Style.RESET_ALL}\n")
    
    finally:
        # Cleanup temporary directory if we cloned a repo
        if cleanup_temp_dir and scan_path and scan_path.exists():
            try:
                shutil.rmtree(scan_path)
                print_info("Cleaned up temporary files")
            except Exception:
                pass  # Ignore cleanup errors


if __name__ == "__main__":
    main()
