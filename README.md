# PyConverter

Universal cross-platform file converter with GUI and CLI.

Supports **images, documents, data files, audio, video**, and includes a full **PDF toolkit**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PySide6](https://img.shields.io/badge/GUI-PySide6-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey)

## Features

### Conversion
- **30+ formats** supported across 5 categories
- **Drag & drop** or browse to add files
- **Batch conversion** with parallel processing (4 threads)
- **Auto-rename** to avoid overwriting existing files
- **File preview** for images, text, and PDFs
- **Queue management** with individual file removal

### Supported Formats

| Category | Input | Output |
|----------|-------|--------|
| **Images** | PNG, JPG, WebP, BMP, TIFF, ICO, GIF | PNG, JPG, WebP, BMP, TIFF, ICO |
| **Documents** | PDF, DOCX, TXT, HTML, Markdown | PDF, DOCX, TXT, HTML |
| **Data** | CSV, JSON, Excel, XML, YAML | CSV, JSON, Excel, XML, YAML |
| **Audio** | MP3, WAV, FLAC, OGG, AAC, WMA, M4A + video files | MP3, WAV, FLAC, OGG, AAC |
| **Video** | MP4, AVI, MKV, WebM, MOV, FLV, WMV, GIF | MP4, AVI, MKV, WebM, GIF |

### PDF Tools (9 tools)
- **Page Editor** - Add, remove, reorder pages with thumbnails
- **Merge** - Combine multiple PDFs
- **Split** - Split into single pages or extract page ranges
- **Rotate** - Rotate pages (90/180/270, all/odd/even/custom)
- **Extract Images** - Save all images from a PDF
- **Images to PDF** - Combine images into a PDF
- **Compress** - Reduce file size with quality control
- **Password** - Encrypt (AES-256) or decrypt PDFs
- **Page Numbers** - Add customizable page numbering

### Additional Tools
- **Watermark** - Text watermark on images and PDFs
- **Watch Folder** - Auto-convert new files in a monitored directory
- **Conversion Profiles** - Save and load preset settings
- **Conversion History** - Track all past conversions

### UI/UX
- **Material Design** theme (dark/light)
- **Keyboard shortcuts** (Ctrl+O, Ctrl+Enter, Delete, Ctrl+T, F1)
- **Desktop notifications** when batch conversion completes
- **Recent files** quick access
- **Bundled ffmpeg** - no system install required for audio/video

## Installation

### From source

```bash
git clone https://github.com/YOUR_USERNAME/pyconverter.git
cd pyconverter
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Run

```bash
# GUI
python main.py

# CLI
python main.py convert image.png -f jpg
python main.py batch *.png -f webp -d output/
python main.py batch -r folder/ -f png -d output/
python main.py formats
```

## CLI Usage

```
python main.py convert <file> -f <format> [-o output] [--option key value]
python main.py batch <files...> -f <format> [-d dir] [-r] [--option key value]
python main.py formats
```

| Option | Description |
|--------|-------------|
| `-f, --format` | Target format (required) |
| `-o, --output` | Output file path (convert only) |
| `-d, --output-dir` | Output directory (batch, default: `.`) |
| `-r, --recursive` | Recurse into directories (batch) |
| `--option KEY VALUE` | Converter option (repeatable) |

### Examples

```bash
# Image conversion with quality
python main.py convert photo.png -f jpg --option quality 90

# Batch convert with resize
python main.py batch *.png -f webp --option resize_width 1920

# Extract audio from video
python main.py convert video.mp4 -f mp3 --option bitrate 320

# Convert all files in a folder recursively
python main.py batch -r ./documents/ -f pdf -d ./output/
```

## Building

See [BUILD.md](BUILD.md) for instructions on building standalone executables for Windows and Linux.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Add files |
| `Ctrl+Enter` | Start conversion |
| `Delete` | Remove selected from queue |
| `Ctrl+T` | Toggle theme |
| `Ctrl+Q` | Exit |
| `F1` | Help |

## Project Structure

```
pyconverter/
├── core/           # Business logic (no Qt dependency)
│   ├── base_converter.py   # BaseConverter ABC
│   ├── registry.py         # ConverterRegistry
│   ├── format_detector.py  # File format detection
│   ├── ffmpeg.py           # Bundled ffmpeg resolution
│   ├── profiles.py         # Conversion profiles
│   ├── history.py          # Conversion history
│   └── watcher.py          # Folder watcher
├── converters/     # Format converters (plugin pattern)
│   ├── image.py    # Pillow
│   ├── document.py # python-docx, PyMuPDF, reportlab
│   ├── data.py     # pandas
│   ├── audio.py    # pydub + ffmpeg
│   └── video.py    # ffmpeg
├── gui/            # PySide6 GUI
│   ├── main_window.py
│   ├── pdf_editor_dialog.py  # 9 PDF tools
│   ├── icons.py              # SVG Material Design icons
│   ├── theme.py              # Dark/light themes
│   └── ...
├── cli/            # Command-line interface
└── resources/      # Icons, styles
```

## License

MIT License - see [LICENSE](LICENSE).
