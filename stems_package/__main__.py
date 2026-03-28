import sys
import os

# Fix SSL certificate issues on macOS - use certifi bundle
if sys.platform == "darwin":
    try:
        import certifi
        cert_path = certifi.where()
        os.environ['SSL_CERT_FILE'] = cert_path
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
        os.environ['CURL_CA_BUNDLE'] = cert_path
    except ImportError:
        pass

# Ensure stdin is a tty for Rich prompts
if not sys.stdin.isatty():
    import io
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, errors='replace')

from pathlib import Path
from tkinter import filedialog
import tkinter as tk

from stems_package.ui import (
    console,
    select_source,
    select_stem_preset,
    select_custom_stems,
    select_model,
    select_output_format,
    show_banner,
    show_error,
    show_info,
    show_processing_progress,
    show_success,
    show_warning,
)
from stems_package.separator import separate_audio
from stems_package.youtube import download_youtube_audio, is_youtube_url


def select_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()
    
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[
            ("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
            ("MP3 Files", "*.mp3"),
            ("WAV Files", "*.wav"),
            ("FLAC Files", "*.flac"),
            ("All Files", "*.*"),
        ],
    )
    
    root.destroy()
    
    return file_path if file_path else None


def get_youtube_url():
    from rich.prompt import Prompt
    
    console.print()
    url = Prompt.ask("[bold cyan]Enter YouTube URL[/bold cyan]", default="")
    
    if not url.strip():
        show_warning("No URL provided.")
        return None
    
    if not is_youtube_url(url):
        show_warning("That doesn't look like a YouTube URL.")
        return None
    
    return url.strip()


def run_interactive():
    while True:
        show_banner()
        source = select_source()
        
        input_path = None
        
        if source == "file":
            console.print()
            show_info("Opening file picker...")
            input_path = select_file()
            
            if not input_path:
                show_warning("No file selected.")
                continue
        elif source == "youtube":
            input_path = get_youtube_url()
            
            if not input_path:
                continue
            
            try:
                show_info("Downloading audio from YouTube...")
                downloads_dir = Path.home() / "Downloads"
                input_path = download_youtube_audio(input_path, str(downloads_dir))
            except Exception as e:
                show_error(f"Failed to download: {e}")
                continue
        
        if input_path is None:
            continue
        
        input_path = Path(input_path)
        
        if not input_path.exists():
            show_error(f"File not found: {input_path}")
            continue
        
        console.print(f"[green]Selected:[/green] {input_path.name}")
        
        stem_config = select_stem_preset()
        
        if stem_config == "back":
            continue
        
        custom_stems = None
        if stem_config == "custom":
            custom_stems = select_custom_stems()
        
        model_choice = select_model()
        
        if model_choice == "back":
            continue
        
        output_format = select_output_format()
        
        output_dir = input_path.parent
        
        console.print()
        show_info(f"Processing with {model_choice} ({output_format})...")
        
        try:
            with show_processing_progress() as progress:
                def update_progress(pct):
                    progress.update_progress(pct)
                
                result = separate_audio(
                    input_path=str(input_path),
                    output_dir=str(output_dir),
                    model_name=model_choice,
                    output_format=output_format,
                    stem_config=stem_config,
                    custom_stems=custom_stems,
                    progress_callback=update_progress,
                )
            
            if result:
                show_success(list(result.values()))
            else:
                show_warning("Processing completed but no output files found.")
        
        except Exception as e:
            show_error(f"Separation failed: {e}")
            continue
        
        from rich.prompt import Confirm
        
        again = Confirm.ask("[bold cyan]Process another file?[/bold cyan]", default=True)
        
        if not again:
            console.print()
            console.print("[cyan]Thanks for using actuallystems![/cyan]")
            console.print()
            break


def main():
    try:
        run_interactive()
    except KeyboardInterrupt:
        console.print()
        console.print("[yellow]Interrupted. Goodbye![/yellow]")
        sys.exit(0)
    except EOFError:
        console.print()
        console.print("[yellow]Input ended. Make sure you're running in an interactive terminal.[/yellow]")
        sys.exit(0)
    except Exception as e:
        show_error(f"Unexpected error: {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()