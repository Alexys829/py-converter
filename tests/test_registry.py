from pyconverter.core.registry import ConverterRegistry
from pyconverter.core.exceptions import ConverterNotFoundError
import pytest


def test_find_image_converter():
    conv = ConverterRegistry.find_converter("png", "jpg")
    assert conv.name() == "Image Converter"


def test_find_converter_not_found():
    with pytest.raises(ConverterNotFoundError):
        ConverterRegistry.find_converter("xyz", "abc")


def test_get_output_formats():
    formats = ConverterRegistry.get_output_formats("png")
    assert "jpg" in formats
    assert "webp" in formats


def test_get_all_input_formats():
    formats = ConverterRegistry.get_all_input_formats()
    assert "png" in formats
    assert "jpg" in formats


def test_list_converters():
    converters = ConverterRegistry.list_converters()
    assert len(converters) > 0
    names = [c.name() for c in converters]
    assert "Image Converter" in names
