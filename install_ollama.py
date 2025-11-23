"""
Quick Ollama installer for Windows.
Run this script to automatically download and install Ollama.
"""

import os
import subprocess
import sys
import urllib.request
from pathlib import Path

def download_ollama():
    """Download Ollama installer."""
    print("📥 Downloading Ollama installer...")
    
    download_url = "https://ollama.com/download/OllamaSetup.exe"
    temp_dir = Path(os.environ['TEMP'])
    installer_path = temp_dir / "OllamaSetup.exe"
    
    try:
        urllib.request.urlretrieve(download_url, installer_path)
        print(f"✓ Downloaded to: {installer_path}")
        return installer_path
    except Exception as e:
        print(f"✗ Download failed: {e}")
        print("\nPlease download manually from: https://ollama.com/download/windows")
        return None

def install_ollama(installer_path):
    """Run Ollama installer."""
    print("\n🔧 Installing Ollama...")
    print("Please follow the installation wizard...")
    
    try:
        subprocess.run([str(installer_path)], check=True)
        print("✓ Installation complete!")
        return True
    except Exception as e:
        print(f"✗ Installation failed: {e}")
        return False

def verify_ollama():
    """Verify Ollama installation."""
    print("\n🔍 Verifying Ollama installation...")
    
    try:
        result = subprocess.run(
            ['ollama', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ Ollama is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("⚠ Ollama command not found. You may need to restart your terminal.")
        return False
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def pull_model(model_name="llama2"):
    """Pull Ollama model."""
    print(f"\n📦 Pulling {model_name} model...")
    print("This may take several minutes (model is ~4GB)...")
    
    try:
        subprocess.run(['ollama', 'pull', model_name], check=True)
        print(f"✓ Model {model_name} downloaded successfully!")
        return True
    except Exception as e:
        print(f"✗ Failed to pull model: {e}")
        return False

def main():
    print("=" * 70)
    print("Ollama Installer for Dev-Standup")
    print("=" * 70)
    
    # Check if already installed
    if verify_ollama():
        print("\n✓ Ollama is already installed!")
        choice = input("\nWould you like to pull a model? (y/n): ")
        if choice.lower() == 'y':
            model = input("Enter model name (llama2/mistral/phi) [llama2]: ").strip() or "llama2"
            pull_model(model)
    else:
        # Download installer
        installer_path = download_ollama()
        if not installer_path:
            sys.exit(1)
        
        # Install
        if install_ollama(installer_path):
            print("\n⚠ Please restart your terminal and run this script again to pull a model.")
            print("\nOr manually run:")
            print("  ollama pull llama2")
    
    print("\n" + "=" * 70)
    print("Setup Complete!")
    print("=" * 70)
    print("\nNow you can use Dev-Standup:")
    print("  python run.py --repo https://github.com/user/repo --all-authors")
    print("\n")

if __name__ == "__main__":
    main()
