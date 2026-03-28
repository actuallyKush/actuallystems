@echo off
REM actuallystems installer for Windows
REM Run: curl -sL https://raw.githubusercontent.com/actuallyKush/actuallystems/main/install.bat | cmd

echo Installing actuallystems...
echo.

python -m pip install demucs yt-dlp "torch>=2.0.0,<2.2" "torchaudio>=2.0.0,<2.2" rich "numpy<2" --quiet

echo.
echo Installation complete!
echo Run: python -m stems
echo Or: python C:\path\to\stems.py

pause