import json
from pathlib import Path

from pyconverter.core.base_converter import ConversionTask
from pyconverter.core.registry import ConverterRegistry


def test_csv_to_json(tmp_csv, tmp_path):
    output = tmp_path / "output.json"
    conv = ConverterRegistry.find_converter("csv", "json")
    task = ConversionTask(tmp_csv, output, "json", {"orient": "records", "indent": 2})
    result = conv.convert(task)
    assert result.exists()
    data = json.loads(result.read_text())
    assert len(data) == 2
    assert data[0]["name"] == "Alice"


def test_csv_to_xlsx(tmp_csv, tmp_path):
    output = tmp_path / "output.xlsx"
    conv = ConverterRegistry.find_converter("csv", "xlsx")
    task = ConversionTask(tmp_csv, output, "xlsx")
    result = conv.convert(task)
    assert result.exists()


def test_json_to_yaml(tmp_path):
    input_file = tmp_path / "test.json"
    input_file.write_text('[{"a": 1, "b": 2}]')
    output = tmp_path / "output.yaml"
    conv = ConverterRegistry.find_converter("json", "yaml")
    task = ConversionTask(input_file, output, "yaml")
    result = conv.convert(task)
    assert result.exists()
    content = result.read_text()
    assert "a:" in content or "- a:" in content
