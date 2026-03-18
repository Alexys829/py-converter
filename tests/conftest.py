import pytest
from pathlib import Path
from PIL import Image

from pyconverter.core.registry import ConverterRegistry


@pytest.fixture(autouse=True)
def reset_registry():
    ConverterRegistry.clear()
    import pyconverter.converters
    pyconverter.converters._registered = False
    pyconverter.converters.ensure_registered()
    yield
    ConverterRegistry.clear()


@pytest.fixture
def tmp_image(tmp_path) -> Path:
    img = Image.new("RGB", (100, 100), color="red")
    path = tmp_path / "test.png"
    img.save(path)
    return path


@pytest.fixture
def tmp_text(tmp_path) -> Path:
    path = tmp_path / "test.txt"
    path.write_text("Hello, World!\nThis is a test file.", encoding="utf-8")
    return path


@pytest.fixture
def tmp_csv(tmp_path) -> Path:
    path = tmp_path / "test.csv"
    path.write_text("name,age,city\nAlice,30,Rome\nBob,25,Milan\n", encoding="utf-8")
    return path
