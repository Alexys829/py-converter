from pathlib import Path
from PIL import Image

from pyconverter.core.base_converter import ConversionTask
from pyconverter.core.registry import ConverterRegistry


def test_png_to_jpg(tmp_image, tmp_path):
    output = tmp_path / "output.jpg"
    conv = ConverterRegistry.find_converter("png", "jpg")
    task = ConversionTask(tmp_image, output, "jpg", {"quality": 85})
    result = conv.convert(task)
    assert result.exists()
    img = Image.open(result)
    assert img.format == "JPEG"


def test_png_to_webp(tmp_image, tmp_path):
    output = tmp_path / "output.webp"
    conv = ConverterRegistry.find_converter("png", "webp")
    task = ConversionTask(tmp_image, output, "webp", {"quality": 80})
    result = conv.convert(task)
    assert result.exists()


def test_png_to_bmp(tmp_image, tmp_path):
    output = tmp_path / "output.bmp"
    conv = ConverterRegistry.find_converter("png", "bmp")
    task = ConversionTask(tmp_image, output, "bmp")
    result = conv.convert(task)
    assert result.exists()


def test_resize(tmp_image, tmp_path):
    output = tmp_path / "output.png"
    conv = ConverterRegistry.find_converter("png", "png")
    task = ConversionTask(tmp_image, output, "png", {"resize_width": 50, "resize_height": 50})
    result = conv.convert(task)
    img = Image.open(result)
    assert img.size == (50, 50)


def test_progress_callback(tmp_image, tmp_path):
    output = tmp_path / "output.jpg"
    conv = ConverterRegistry.find_converter("png", "jpg")
    task = ConversionTask(tmp_image, output, "jpg")

    progress_values = []
    result = conv.convert(task, progress_callback=lambda p: progress_values.append(p))
    assert result.exists()
    assert 0.0 in progress_values
    assert 1.0 in progress_values
