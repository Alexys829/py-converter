import subprocess
import re
from pathlib import Path
from typing import Callable

from pyconverter.core.base_converter import BaseConverter, ConversionOption, ConversionTask
from pyconverter.core.exceptions import ConversionError
from pyconverter.core.ffmpeg import ffmpeg_available, get_ffmpeg_path, get_ffprobe_path


CODEC_MAP = {
    "mp4": "libx264",
    "avi": "libx264",
    "mkv": "libx264",
    "webm": "libvpx-vp9",
    "gif": "gif",
}


class VideoConverter(BaseConverter):

    def name(self) -> str:
        return "Video Converter"

    def supported_input_formats(self) -> list[str]:
        if not ffmpeg_available():
            return []
        return ["mp4", "avi", "mkv", "webm", "mov", "flv", "wmv", "gif"]

    def supported_output_formats(self) -> list[str]:
        if not ffmpeg_available():
            return []
        return ["mp4", "avi", "mkv", "webm", "gif"]

    def get_options(self, input_format: str, output_format: str) -> list[ConversionOption]:
        opts = []
        if output_format != "gif":
            opts.append(ConversionOption(
                "crf", "Quality (CRF, lower=better)", "int", 23, min_val=0, max_val=51
            ))
            opts.append(ConversionOption(
                "resolution", "Resolution", "choice", "original",
                choices=["original", "1920x1080", "1280x720", "854x480", "640x360"],
            ))
        else:
            opts.append(ConversionOption(
                "fps", "FPS", "int", 15, min_val=1, max_val=60
            ))
            opts.append(ConversionOption(
                "width", "Width (px)", "int", 480, min_val=50, max_val=1920
            ))
        return opts

    def convert(
        self,
        task: ConversionTask,
        progress_callback: Callable[[float], None] | None = None,
    ) -> Path:
        if not ffmpeg_available():
            raise ConversionError("ffmpeg is not available.")

        if progress_callback:
            progress_callback(0.0)

        task.output_path.parent.mkdir(parents=True, exist_ok=True)

        duration = self._get_duration(task.input_path)
        cmd = self._build_command(task)

        if progress_callback:
            progress_callback(0.1)

        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        if duration and progress_callback:
            for line in process.stderr:
                time_match = re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})", line)
                if time_match:
                    h, m, s, cs = [int(x) for x in time_match.groups()]
                    current = h * 3600 + m * 60 + s + cs / 100
                    progress = min(0.1 + (current / duration) * 0.9, 0.99)
                    progress_callback(progress)
        else:
            process.wait()

        process.wait()
        if process.returncode != 0:
            stderr = process.stderr.read() if process.stderr else ""
            raise ConversionError(f"ffmpeg failed (exit {process.returncode}): {stderr[-200:]}")

        if progress_callback:
            progress_callback(1.0)

        return task.output_path

    def _get_duration(self, path: Path) -> float | None:
        ffprobe = get_ffprobe_path()
        if not ffprobe:
            return None
        try:
            result = subprocess.run(
                [ffprobe, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                capture_output=True, text=True, timeout=10,
            )
            return float(result.stdout.strip())
        except Exception:
            return None

    def _build_command(self, task: ConversionTask) -> list[str]:
        ffmpeg = get_ffmpeg_path()
        cmd = [ffmpeg, "-y", "-i", str(task.input_path)]

        out_fmt = task.output_format

        if out_fmt == "gif":
            fps = task.options.get("fps", 15)
            width = task.options.get("width", 480)
            cmd += [
                "-vf", f"fps={fps},scale={width}:-1:flags=lanczos",
                "-loop", "0",
            ]
        else:
            codec = CODEC_MAP.get(out_fmt, "libx264")
            cmd += ["-c:v", codec]

            crf = task.options.get("crf", 23)
            if codec in ("libx264", "libx265"):
                cmd += ["-crf", str(crf)]
            elif codec == "libvpx-vp9":
                cmd += ["-crf", str(crf), "-b:v", "0"]

            resolution = task.options.get("resolution", "original")
            if resolution != "original":
                cmd += ["-s", resolution]

            if out_fmt == "webm":
                cmd += ["-c:a", "libopus"]
            else:
                cmd += ["-c:a", "aac"]

        cmd.append(str(task.output_path))
        return cmd
