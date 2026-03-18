import mimetypes
from pathlib import Path

MAGIC_SIGNATURES: dict[bytes, str] = {
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpg",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
    b"RIFF": "webp",  # RIFF....WEBP
    b"BM": "bmp",
    b"II\x2a\x00": "tiff",
    b"MM\x00\x2a": "tiff",
    b"%PDF": "pdf",
    b"PK\x03\x04": "zip",  # docx, xlsx, epub are ZIP-based
    b"\x00\x00\x01\x00": "ico",
    b"ID3": "mp3",
    b"\xff\xfb": "mp3",
    b"\xff\xf3": "mp3",
    b"fLaC": "flac",
    b"OggS": "ogg",
}

MIME_TO_FORMAT: dict[str, str] = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
    "image/bmp": "bmp",
    "image/tiff": "tiff",
    "image/gif": "gif",
    "image/x-icon": "ico",
    "application/pdf": "pdf",
    "text/plain": "txt",
    "text/html": "html",
    "text/csv": "csv",
    "text/markdown": "md",
    "application/json": "json",
    "application/xml": "xml",
    "text/xml": "xml",
    "application/yaml": "yaml",
    "audio/mpeg": "mp3",
    "audio/wav": "wav",
    "audio/flac": "flac",
    "audio/ogg": "ogg",
    "video/mp4": "mp4",
    "video/x-msvideo": "avi",
    "video/x-matroska": "mkv",
    "video/webm": "webm",
}


def detect_format(file_path: Path) -> str | None:
    # Try magic bytes first
    try:
        with open(file_path, "rb") as f:
            header = f.read(16)
        for signature, fmt in MAGIC_SIGNATURES.items():
            if header.startswith(signature):
                if fmt == "webp" and b"WEBP" in header:
                    return "webp"
                elif fmt != "webp":
                    return fmt
    except (OSError, IOError):
        pass

    # Fall back to extension
    ext = file_path.suffix.lower().lstrip(".")
    if ext:
        return ext

    # Try mimetypes
    mime, _ = mimetypes.guess_type(str(file_path))
    if mime and mime in MIME_TO_FORMAT:
        return MIME_TO_FORMAT[mime]

    return None
