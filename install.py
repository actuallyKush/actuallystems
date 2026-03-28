#!/usr/bin/env python3
"""
actuallystems - Windows Installer
One command to install everything on Windows.

Usage:
    irm https://raw.githubusercontent.com/actuallyKush/actuallystems/main/install.py | python3
    # OR
    python3 -c "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/actuallyKush/actuallystems/main/install.py' -OutFile 'install.py'; python3 install.py"
"""

import os
import sys
import ssl
import subprocess
import platform
import urllib.request
import tempfile
import shutil

REQUIREMENTS = [
    "demucs>=4.0.0",
    "yt-dlp>=2024.0.0",
    "rich>=13.0.0",
    "torch>=2.0.0",
    "torchaudio>=2.0.0",
    "numpy<2",
]

MIN_PYTHON = (3, 10)


def check_python():
    """Check if Python is installed and meets minimum version."""
    try:
        version = sys.version_info
        if version >= MIN_PYTHON:
            return True, None
        return False, f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required, you have {version.major}.{version.minor}"
    except Exception as e:
        return False, str(e)


def check_command(cmd):
    """Check if a command exists."""
    try:
        result = subprocess.run(["where", cmd], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def install_ffmpeg():
    """Install FFmpeg on Windows."""
    print("Installing FFmpeg on Windows...")

    try:
        subprocess.run(["winget", "install", "ffmpeg", "--accept-source-agreements", "--accept-package-agreements"], check=True)
        print("FFmpeg installed successfully!")
        return True
    except Exception as e:
        print(f"Could not auto-install FFmpeg: {e}")
        print("\nPlease install FFmpeg manually:")
        print("  winget install ffmpeg")
        print("  OR download from https://ffmpeg.org/download.html")
        return False


def install_dependencies():
    """Install Python dependencies via pip."""
    print("Installing Python dependencies...")
    print(f"  Packages: {', '.join(REQUIREMENTS)}")
    print()

    try:
        subprocess.run([sys.executable, "-m", "pip", "install"] + REQUIREMENTS, check=True)
        print("\nDependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False


def download_stems():
    """Download the actuallystems source code."""
    print("Downloading actuallystems...")
    url = "https://github.com/actuallyKush/actuallystems/archive/refs/heads/main.zip"

    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "actuallystems.zip")
        
        context = ssl._create_unverified_context() if hasattr(ssl, '_create_unverified_context') else None
        if context:
            urllib.request.urlretrieve(url, zip_path, context=context)
        else:
            urllib.request.urlretrieve(url, zip_path)
        
        import zipfile
        with zipfile.ZipFile(zip_path, "r") as z:
            extract_path = os.path.expanduser("~/actuallystems")
            z.extractall(temp_dir)
            
            extracted_folder = os.path.join(temp_dir, "actuallystems-main")
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
            shutil.move(extracted_folder, extract_path)
        
        shutil.rmtree(temp_dir)
        print(f"Downloaded to: {extract_path}")
        return extract_path
    except Exception as e:
        print(f"Failed to download: {e}")
        return None


def main():
    print("=" * 60)
    print("  actuallystems - Windows Installer")
    print("=" * 60)
    print()

    # Check Python
    python_ok, python_error = check_python()
    if not python_ok:
        print(f"Error: {python_error}")
        print("\nPlease install Python first:")
        print("  winget install Python.Python.3.12")
        return 1

    print(f"Python version: {sys.version.split()[0]}")

    # Check FFmpeg
    if not check_command("ffmpeg"):
        print("\nFFmpeg not found.")
        install_ffmpeg()
    else:
        print("FFmpeg: Found")

    # Install dependencies
    print()
    if not install_dependencies():
        print("\nInstallation failed. Try installing manually:")
        print(f"  pip install {' '.join(REQUIREMENTS)}")
        return 1

    # Download source
    print()
    install_path = download_stems()

    # Install package in editable mode so 'actuallystems' CLI command works
    if install_path:
        install_path = os.path.expanduser(install_path)
        print(f"\nRegistering 'actuallystems' command...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", install_path],
            check=True,
            cwd=install_path
        )

    print()
    print("=" * 60)
    print("  Installation Complete!")
    print("=" * 60)
    print()
    print("To run actuallystems:")
    if install_path:
        print(f"  cd {install_path}")
        print("  python stems.py")
    print("  OR (if installed via pip): actuallystems")
    print()
    print("For help: https://github.com/actuallyKush/actuallystems")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
