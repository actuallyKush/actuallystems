# actuallystems

A free, open-source CLI tool for music producers to separate audio into stems (vocals, drums, bass, synths).

## What is Stem Separation?

Stem separation (also known as "demixing" or "source separation") is the process of splitting a complete audio mix into its individual components - typically vocals, drums, bass, and synths.

### Common Use Cases:
- **Create instrumentals** - Remove vocals for karaoke or remixing
- **Extract vocals** - Get the vocal track for sampling or remix
- **Remix production** - Isolate elements to create new tracks
- **Music practice** - Isolate drums or bass for learning
- **Audio engineering** - Analyze individual track elements

## Features

- Extract vocals from any audio file
- Full 4-stem separation (vocals, drums, bass, synths)
- Download audio directly from YouTube
- Supports WAV (lossless) and MP3 output formats
- Two model options: fast (htdemucs) and quality (htdemucs_ft)
- Simple interactive TUI - no technical knowledge required
- GPU acceleration support for faster processing
- **One-command install** - automatically installs all dependencies

## Requirements

- Python 3.10+
- FFmpeg
- 4GB+ RAM recommended
- ~2GB disk space for ML models

## Installation

### One Command Install (Windows)
```powershell
irm https://raw.githubusercontent.com/actuallyKush/actuallystems/main/install.py | python3
```

### One Command Install (Mac/Linux)
```bash
curl -sL https://raw.githubusercontent.com/actuallyKush/actuallystems/main/install.py | python3
```

### From Source
```bash
git clone https://github.com/actuallyKush/actuallystems.git
cd actuallystems
pip install -e .
```

After installation, run:
```bash
actuallystems
```

## Usage

```bash
actuallystems
```

The tool will guide you through:

1. **Select audio source** - Choose a file from your computer or enter a YouTube URL
2. **Choose separation type** - Vocals only (faster) or full 4-stem separation
3. **Select model** - htdemucs (faster) or htdemucs_ft (better quality, slower)
4. **Choose format** - WAV (lossless) or MP3 (smaller files)

## Output

Separated stems are saved in the same folder as your input file:

```
YourSong.mp3
├── vocals.wav
├── drums.wav
├── bass.wav
└── synths.wav
```

## Troubleshooting

### "FFmpeg is not installed"
```powershell
winget install ffmpeg    # Windows
brew install ffmpeg      # macOS
sudo apt install ffmpeg  # Linux
```

### "No GPU detected - Running on CPU"
This is normal. The tool will work but run slower on CPU. For faster processing, use a GPU with CUDA.

### "TorchCodec errors"
```bash
pip install torchcodec
```

## How It Works

actuallystems uses **Demucs** (Deep Encoder Decoder for Music Source Separation), an open-source neural network developed by Meta AI (Facebook Research). It uses state-of-the-art deep learning to analyze and separate audio signals into distinct components.

- **htdemucs**: Hybrid Transformer Demucs - fast, good quality
- **htdemucs_ft**: Fine-tuned version - best quality, slower

## License

MIT License - Free to use, modify, and distribute.

---

Star this project if you find it useful!