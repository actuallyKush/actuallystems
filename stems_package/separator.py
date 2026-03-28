import os
import subprocess
import sys

# Fix SSL certificate issues on macOS - use certifi bundle (global fix)
if sys.platform == "darwin":
    try:
        import certifi
        cert_path = certifi.where()
        os.environ['SSL_CERT_FILE'] = cert_path
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
        os.environ['CURL_CA_BUNDLE'] = cert_path
    except ImportError:
        pass

from pathlib import Path
from typing import List, Dict, Optional

import torch
from rich.console import Console

console = Console()


class StemSeparator:
    def __init__(self, model_name: str = "htdemucs", output_format: str = "wav"):
        self.model_name = model_name
        self.output_format = output_format
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # For macOS, add SSL env vars to subprocess
        self.env = os.environ.copy()
        if sys.platform == "darwin":
            try:
                import certifi
                self.env['SSL_CERT_FILE'] = certifi.where()
                self.env['REQUESTS_CA_BUNDLE'] = certifi.where()
            except ImportError:
                pass
        
        if self.device == "cpu":
            console.print("[yellow]Warning: No GPU detected. Running on CPU (slower).[/yellow]")
    
    def separate(
        self,
        input_path: str,
        output_dir: Optional[str] = None,
        stem_config: str = "full",
        custom_stems: Optional[List[str]] = None,
        progress_callback=None,
    ) -> Dict[str, str]:
        input_path = Path(input_path)
        
        if output_dir is None:
            output_dir = input_path.parent
        
        output_dir = Path(output_dir)
        
        if stem_config == "vocals_only":
            cmd = self._build_vocals_only_cmd(input_path, output_dir)
            expected_stems = ["vocals", "no_vocals"]
        elif stem_config == "full":
            cmd = self._build_full_cmd(input_path, output_dir)
            expected_stems = ["vocals", "drums", "bass", "synths"]
        elif stem_config == "custom" and custom_stems:
            if "vocals" in custom_stems and len(custom_stems) == 1:
                cmd = self._build_vocals_only_cmd(input_path, output_dir)
                expected_stems = ["vocals", "no_vocals"]
            elif "vocals" in custom_stems:
                cmd = self._build_custom_cmd(input_path, output_dir, custom_stems)
                expected_stems = custom_stems
            else:
                cmd = self._build_full_cmd(input_path, output_dir)
                expected_stems = ["vocals", "drums", "bass", "synths"]
        else:
            cmd = self._build_full_cmd(input_path, output_dir)
            expected_stems = ["vocals", "drums", "bass", "synths"]
        
        result = self._run_command(cmd, progress_callback)
        
        if result != 0:
            raise RuntimeError(f"Separation failed with exit code {result}")
        
        output_files = self._find_output_files(input_path, output_dir, expected_stems)
        
        return output_files
    
    def _build_vocals_only_cmd(self, input_path: Path, output_dir: Path) -> List[str]:
        cmd = [
            sys.executable,
            "-m",
            "demucs",
            "--two-stems",
            "vocals",
            "-n",
            self.model_name,
            "-o",
            str(output_dir),
        ]
        
        if self.output_format == "mp3":
            cmd.append("--mp3")
        
        if self.device == "cpu":
            cmd.extend(["-d", "cpu"])
        
        cmd.append(str(input_path))
        
        return cmd
    
    def _build_full_cmd(self, input_path: Path, output_dir: Path) -> List[str]:
        cmd = [
            sys.executable,
            "-m",
            "demucs",
            "-n",
            self.model_name,
            "-o",
            str(output_dir),
        ]
        
        if self.output_format == "mp3":
            cmd.append("--mp3")
        
        if self.device == "cpu":
            cmd.extend(["-d", "cpu"])
        
        cmd.append(str(input_path))
        
        return cmd
    
    def _build_custom_cmd(
        self, input_path: Path, output_dir: Path, custom_stems: List[str]
    ) -> List[str]:
        cmd = [
            sys.executable,
            "-m",
            "demucs",
            "-n",
            self.model_name,
            "-o",
            str(output_dir),
        ]
        
        if self.output_format == "mp3":
            cmd.append("--mp3")
        
        if self.device == "cpu":
            cmd.extend(["-d", "cpu"])
        
        cmd.append(str(input_path))
        
        return cmd
    
    def _run_command(self, cmd: List[str], progress_callback=None) -> int:
        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
        
        # Force unbuffered output for progress updates
        env = self.env.copy()
        env["PYTHONUNBUFFERED"] = "1"
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",
            env=env,
            cwd=os.getcwd(),
            universal_newlines=True,
        )
        
        output_lines = []
        import re
        pattern = re.compile(r'(\d+)%')
        
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                line = line.strip()
                output_lines.append(line)
                if progress_callback:
                    if "Separating" in line:
                        progress_callback(10)
                    else:
                        match = pattern.search(line)
                        if match:
                            pct = int(match.group(1))
                            progress_callback(min(pct, 95))
        
        if progress_callback:
            progress_callback(100)
        
        if process.returncode != 0:
            console.print("[red]Error output:[/red]")
            for line in output_lines[-20:]:
                console.print(f"[red]{line.rstrip()}[/red]")
        
        return process.returncode
    
    def _find_output_files(
        self, input_path: Path, output_dir: Path, expected_stems: List[str]
    ) -> Dict[str, str]:
        output_files = {}
        
        stem_dir = output_dir / input_path.stem
        
        if not stem_dir.exists():
            if self.model_name == "htdemucs_ft":
                stem_dir = output_dir / "htdemucs_ft" / input_path.stem
            elif self.model_name == "htdemucs":
                stem_dir = output_dir / "htdemucs" / input_path.stem
        
        if stem_dir.exists():
            stem_mapping = {"synths": "other"}
            
            for stem in expected_stems:
                file_stem = stem_mapping.get(stem, stem)
                
                if stem == "no_vocals":
                    stem_file = stem_dir / f"no_vocals.{self.output_format}"
                    output_files["instrumental"] = str(stem_file)
                else:
                    stem_file = stem_dir / f"{file_stem}.{self.output_format}"
                    if stem_file.exists():
                        output_files[stem] = str(stem_file)
        
        return output_files


def separate_audio(
    input_path: str,
    output_dir: Optional[str] = None,
    model_name: str = "htdemucs",
    output_format: str = "wav",
    stem_config: str = "full",
    custom_stems: Optional[List[str]] = None,
    progress_callback=None,
) -> Dict[str, str]:
    separator = StemSeparator(model_name, output_format)
    
    return separator.separate(
        input_path=input_path,
        output_dir=output_dir,
        stem_config=stem_config,
        custom_stems=custom_stems,
        progress_callback=progress_callback,
    )