from pathlib import Path
from typing import Callable

from PIL import Image

from pyconverter.core.base_converter import BaseConverter, ConversionOption, ConversionTask


FORMAT_SAVE_MAP = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "bmp": "BMP",
    "tiff": "TIFF",
    "tif": "TIFF",
    "ico": "ICO",
}


class ImageConverter(BaseConverter):

    def name(self) -> str:
        return "Image Converter"

    def supported_input_formats(self) -> list[str]:
        return ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "tif", "ico", "gif"]

    def supported_output_formats(self) -> list[str]:
        return ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "ico"]

    def get_options(self, input_format: str, output_format: str) -> list[ConversionOption]:
        opts = []
        if output_format in ("jpg", "jpeg", "webp"):
            opts.append(ConversionOption(
                "quality", "Quality (%)", "int", 85, min_val=1, max_val=100
            ))
        if output_format == "png":
            opts.append(ConversionOption(
                "compress_level", "PNG Compression (0-9)", "int", 6, min_val=0, max_val=9
            ))
        opts.append(ConversionOption(
            "optimize", "Optimize file size", "bool", True
        ))
        opts.append(ConversionOption(
            "resize_width", "Resize Width (px, 0=keep)", "int", 0, min_val=0, max_val=10000
        ))
        opts.append(ConversionOption(
            "resize_height", "Resize Height (px, 0=keep)", "int", 0, min_val=0, max_val=10000
        ))
        return opts

    def convert(
        self,
        task: ConversionTask,
        progress_callback: Callable[[float], None] | None = None,
    ) -> Path:
        if progress_callback:
            progress_callback(0.0)

        img = Image.open(task.input_path)

        # Handle resize
        w = task.options.get("resize_width", 0)
        h = task.options.get("resize_height", 0)
        if w or h:
            orig_w, orig_h = img.size
            if w and not h:
                h = int(orig_h * (w / orig_w))
            elif h and not w:
                w = int(orig_w * (h / orig_h))
            img = img.resize((w, h), Image.Resampling.LANCZOS)

        # Handle format-specific options
        save_kwargs: dict = {}
        pil_format = FORMAT_SAVE_MAP.get(task.output_format, task.output_format.upper())

        if task.output_format in ("jpg", "jpeg"):
            save_kwargs["quality"] = task.options.get("quality", 85)
            save_kwargs["optimize"] = task.options.get("optimize", True)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
        elif task.output_format == "webp":
            save_kwargs["quality"] = task.options.get("quality", 85)
        elif task.output_format == "png":
            save_kwargs["optimize"] = task.options.get("optimize", True)
            save_kwargs["compress_level"] = task.options.get("compress_level", 6)
        elif task.output_format == "ico":
            sizes = [(min(img.size[0], 256), min(img.size[1], 256))]
            save_kwargs["sizes"] = sizes

        if progress_callback:
            progress_callback(0.5)

        task.output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(task.output_path, format=pil_format, **save_kwargs)

        if progress_callback:
            progress_callback(1.0)

        return task.output_path
