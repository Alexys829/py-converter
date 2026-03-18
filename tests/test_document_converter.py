from pathlib import Path

from pyconverter.core.base_converter import ConversionTask
from pyconverter.core.registry import ConverterRegistry


def test_txt_to_html(tmp_text, tmp_path):
    output = tmp_path / "output.html"
    conv = ConverterRegistry.find_converter("txt", "html")
    task = ConversionTask(tmp_text, output, "html")
    result = conv.convert(task)
    assert result.exists()
    content = result.read_text()
    assert "Hello, World!" in content
    assert "<html>" in content


def test_txt_to_pdf(tmp_text, tmp_path):
    output = tmp_path / "output.pdf"
    conv = ConverterRegistry.find_converter("txt", "pdf")
    task = ConversionTask(tmp_text, output, "pdf")
    result = conv.convert(task)
    assert result.exists()
    assert result.stat().st_size > 0
