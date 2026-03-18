"""Centralized ffmpeg path resolution.

Priority:
1. Bundled ffmpeg via imageio-ffmpeg (no system dependency needed)
2. System ffmpeg (fallback)
"""
import os
import shutil

_ffmpeg_path: str | None = None
_ffprobe_path: str | None = None


def get_ffmpeg_path() -> str | None:
    """Return the path to ffmpeg binary, or None if unavailable."""
    global _ffmpeg_path
    if _ffmpeg_path is not None:
        return _ffmpeg_path

    # Try bundled ffmpeg first
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path and os.path.isfile(path):
            _ffmpeg_path = path
            return _ffmpeg_path
    except (ImportError, RuntimeError):
        pass

    # Fallback to system ffmpeg
    system_path = shutil.which("ffmpeg")
    if system_path:
        _ffmpeg_path = system_path
        return _ffmpeg_path

    return None


def get_ffprobe_path() -> str | None:
    """Return the path to ffprobe binary, or None if unavailable."""
    global _ffprobe_path
    if _ffprobe_path is not None:
        return _ffprobe_path

    # ffprobe is next to ffmpeg in imageio-ffmpeg
    ffmpeg = get_ffmpeg_path()
    if ffmpeg:
        ffmpeg_dir = os.path.dirname(ffmpeg)
        for name in ("ffprobe", "ffprobe.exe"):
            candidate = os.path.join(ffmpeg_dir, name)
            if os.path.isfile(candidate):
                _ffprobe_path = candidate
                return _ffprobe_path

    # Fallback to system ffprobe
    system_path = shutil.which("ffprobe")
    if system_path:
        _ffprobe_path = system_path
        return _ffprobe_path

    return None


def ffmpeg_available() -> bool:
    """Check if ffmpeg is available (bundled or system)."""
    return get_ffmpeg_path() is not None


def configure_pydub():
    """Configure pydub to use our ffmpeg path."""
    ffmpeg = get_ffmpeg_path()
    ffprobe = get_ffprobe_path()
    if ffmpeg:
        from pydub import AudioSegment
        AudioSegment.converter = ffmpeg
        if ffprobe:
            AudioSegment.ffprobe = ffprobe
