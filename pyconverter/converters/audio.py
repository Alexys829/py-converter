from pathlib import Path
from typing import Callable

from pyconverter.core.base_converter import BaseConverter, ConversionOption, ConversionTask
from pyconverter.core.exceptions import ConversionError
from pyconverter.core.ffmpeg import ffmpeg_available, configure_pydub


class AudioConverter(BaseConverter):

    def name(self) -> str:
        return "Audio Converter"

    def supported_input_formats(self) -> list[str]:
        if not ffmpeg_available():
            return []
        return ["mp3", "wav", "flac", "ogg", "aac", "wma", "m4a",
                "mp4", "avi", "mkv", "webm", "mov", "flv"]

    def supported_output_formats(self) -> list[str]:
        if not ffmpeg_available():
            return []
        return ["mp3", "wav", "flac", "ogg", "aac"]

    def get_options(self, input_format: str, output_format: str) -> list[ConversionOption]:
        opts = []
        if output_format == "mp3":
            opts.append(ConversionOption(
                "bitrate", "Bitrate (kbps)", "choice", "192",
                choices=["128", "192", "256", "320"],
            ))
        if output_format in ("mp3", "wav", "flac", "ogg", "aac"):
            opts.append(ConversionOption(
                "sample_rate", "Sample Rate (Hz)", "choice", "44100",
                choices=["22050", "44100", "48000", "96000"],
            ))
            opts.append(ConversionOption(
                "channels", "Channels", "choice", "2",
                choices=["1", "2"],
            ))
        return opts

    def convert(
        self,
        task: ConversionTask,
        progress_callback: Callable[[float], None] | None = None,
    ) -> Path:
        if not ffmpeg_available():
            raise ConversionError("ffmpeg is not available.")

        configure_pydub()

        if progress_callback:
            progress_callback(0.0)

        from pydub import AudioSegment

        task.output_path.parent.mkdir(parents=True, exist_ok=True)

        in_fmt = task.input_path.suffix.lower().lstrip(".")
        audio = AudioSegment.from_file(str(task.input_path), format=in_fmt)

        if progress_callback:
            progress_callback(0.3)

        # Apply options
        sample_rate = int(task.options.get("sample_rate", 44100))
        channels = int(task.options.get("channels", 2))
        audio = audio.set_frame_rate(sample_rate).set_channels(channels)

        if progress_callback:
            progress_callback(0.5)

        # Export
        export_kwargs: dict = {"format": task.output_format}
        if task.output_format == "mp3":
            bitrate = task.options.get("bitrate", "192")
            export_kwargs["bitrate"] = f"{bitrate}k"

        audio.export(str(task.output_path), **export_kwargs)

        if progress_callback:
            progress_callback(1.0)

        return task.output_path
