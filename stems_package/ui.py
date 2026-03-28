import sys
import os

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()

def show_banner():
    print()
    print("██████╗  ██████╗████████╗██╗   ██╗ █████╗ ██╗     ██╗  ██╗   ██╗███████╗████████╗███████╗███╗   ███╗███████╗")
    print("██╔══██╗██╔════╝╚══██╔══╝██║   ██║██╔══██╗██║     ██║  ╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║██╔════╝")
    print("███████║██║        ██║   ██║   ██║███████║██║     ██║   ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║███████╗")
    print("██╔══██║██║        ██║   ██║   ██║██╔══██║██║     ██║    ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║╚════██║")
    print("██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║███████╗███████╗██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║███████║")
    print("╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝╚══════╝")
    print()
    print("       actuallystems - Stem Splitter v1.0.0")
    print()


def show_main_menu():
    console.print()
    console.print("[bold cyan]What would you like to do?[/bold cyan]")
    console.print()
    console.print("  [1] [bold]Select Audio File[/bold] - Choose a file from your computer")
    console.print("  [2] [bold]YouTube URL[/bold] - Download and process from YouTube")
    console.print("  [3] [bold]Exit[/bold]")
    console.print()


def select_source():
    show_main_menu()
    
    while True:
        choice = Prompt.ask("[bold cyan]Choose an option[/bold cyan]", choices=["1", "2", "3"], default="1")
        
        if choice == "1":
            return "file"
        elif choice == "2":
            return "youtube"
        elif choice == "3":
            console.print("[yellow]Goodbye![/yellow]")
            sys.exit(0)


def select_stem_preset():
    console.print()
    console.print("[bold cyan]How would you like to separate the audio?[/bold cyan]")
    console.print()
    console.print("  [1] [bold]Vocals Only[/bold] - Extract vocals + instrumental")
    console.print("  [2] [bold]Full Separation[/bold] - Vocals, drums, bass, synths")
    console.print("  [3] [bold]Custom[/bold] - Choose specific stems")
    console.print("  [4] [bold]Back[/bold]")
    console.print()
    
    while True:
        choice = Prompt.ask("[bold cyan]Choose preset[/bold cyan]", choices=["1", "2", "3", "4"], default="1")
        
        if choice == "1":
            return "vocals_only"
        elif choice == "2":
            return "full"
        elif choice == "3":
            return "custom"
        elif choice == "4":
            return "back"


def select_custom_stems():
    console.print()
    console.print("[bold cyan]Select stems to extract:[/bold cyan]")
    console.print()
    
    stems = []
    
    vocals = Confirm.ask("  [ ] [bold]Vocals[/bold]", default=True)
    if vocals:
        stems.append("vocals")
    
    drums = Confirm.ask("  [ ] [bold]Drums[/bold]", default=False)
    if drums:
        stems.append("drums")
    
    bass = Confirm.ask("  [ ] [bold]Bass[/bold]", default=False)
    if bass:
        stems.append("bass")
    
    synths = Confirm.ask("  [ ] [bold]Synths[/bold]", default=False)
    if synths:
        stems.append("synths")
    
    if not stems:
        show_warning("No stems selected. Using full separation.")
        return None
    
    return stems


def select_model():
    console.print()
    console.print("[bold cyan]Select model:[/bold cyan]")
    console.print()
    console.print("  [1] [bold]htdemucs[/bold] - Faster processing")
    console.print("  [2] [bold]htdemucs_ft[/bold] - Best quality (slower)")
    console.print("  [3] [bold]Back[/bold]")
    console.print()
    
    while True:
        choice = Prompt.ask("[bold cyan]Choose model[/bold cyan]", choices=["1", "2", "3"], default="1")
        
        if choice == "1":
            return "htdemucs"
        elif choice == "2":
            return "htdemucs_ft"
        elif choice == "3":
            return "back"


def select_output_format():
    console.print()
    console.print("[bold cyan]Select output format:[/bold cyan]")
    console.print()
    console.print("  [1] [bold]WAV[/bold] - Lossless quality")
    console.print("  [2] [bold]MP3[/bold] - Smaller file size")
    console.print()
    
    while True:
        choice = Prompt.ask("[bold cyan]Choose output format[/bold cyan]", choices=["1", "2"], default="1")
        
        if choice == "1":
            return "wav"
        elif choice == "2":
            return "mp3"


def show_info(message):
    console.print(f"[cyan]{message}[/cyan]")


def show_warning(message):
    console.print(f"[yellow]Warning: {message}[/yellow]")


def show_error(message):
    console.print(Panel(f"[red]Error: {message}[/red]", border_style="red"))


def show_success(files):
    console.print(Panel("[bold green]Separation Complete![/bold green]", border_style="green"))
    console.print()
    console.print("[bold green]Stems saved:[/bold green]")
    for f in files:
        display_path = f.replace("\\", "/").replace("/other.wav", "/synths.wav")
        console.print(f"  - {display_path}")


class LiveProgress:
    def __init__(self):
        self.progress = None
        self.task = None
        self._stop = False
        self._last_update = 0
        
    def __enter__(self):
        from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn
        from rich.console import Console
        
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("{task.elapsed}"),
            console=Console(),
        )
        self.progress.start()
        self.task = self.progress.add_task("[cyan]Separating audio...", total=100)
        
        self._last_update = 0
        return self
    
    def update_progress(self, value):
        if self.progress and self.task is not None and value > self._last_update:
            self.progress.update(self.task, completed=value)
            self._last_update = value
        
    def __exit__(self, *args):
        if self.progress and self.task is not None:
            self.progress.update(self.task, completed=100)
        if self.progress:
            self.progress.stop()


def show_processing_progress():
    return LiveProgress()