import os
import tempfile
from pathlib import Path
from typing import Optional

import yt_dlp

import sys
import os as _os
_stems_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _stems_dir)
from ui import console, show_processing_progress


def download_youtube_audio(url: str, output_dir: Optional[str] = None) -> str:
    if output_dir is None:
        output_dir = tempfile.gettempdir()
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        "quiet": False,
        "no_warnings": False,
    }
    
    console.print(f"[cyan]Downloading: {url}[/cyan]")
    
    with show_processing_progress() as progress:
        task = progress.add_task("[cyan]Downloading from YouTube...", total=100)
        
        def progress_hook(d):
            if d["status"] == "downloading":
                percent = d.get("_percent_str", "0%")
                try:
                    p = float(percent.rstrip("%"))
                    progress.update(task, completed=p / 2)
                except:
                    pass
            elif d["status"] == "finished":
                progress.update(task, completed=50)
        
        ydl_opts["progress_hooks"] = [progress_hook]
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            filename = ydl.prepare_filename(info)
            filename = Path(filename)
            
            if filename.suffix != ".wav":
                filename = filename.with_suffix(".wav")
            
            progress.update(task, completed=100)
    
    console.print(f"[green]Downloaded: {filename.name}[/green]")
    
    return str(filename)


def is_youtube_url(url: str) -> bool:
    youtube_domains = [
        "youtube.com",
        "youtu.be",
        "youtube-nocookie.com",
        "music.youtube.com",
    ]
    
    url_lower = url.lower()
    
    for domain in youtube_domains:
        if domain in url_lower:
            return True
    
    return url.lower().startswith("yt:") or url.lower().startswith("youtube:")