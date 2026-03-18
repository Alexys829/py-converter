import json
from pathlib import Path
from typing import Callable

from pyconverter.core.base_converter import BaseConverter, ConversionOption, ConversionTask
from pyconverter.core.exceptions import ConversionError


class DataConverter(BaseConverter):

    def name(self) -> str:
        return "Data Converter"

    def supported_input_formats(self) -> list[str]:
        return ["csv", "json", "xlsx", "xls", "xml", "yaml", "yml"]

    def supported_output_formats(self) -> list[str]:
        return ["csv", "json", "xlsx", "xml", "yaml"]

    def get_options(self, input_format: str, output_format: str) -> list[ConversionOption]:
        opts = []
        if output_format == "csv":
            opts.append(ConversionOption(
                "separator", "Separator", "choice", ",",
                choices=[",", ";", "\t", "|"],
            ))
        if output_format == "json":
            opts.append(ConversionOption(
                "orient", "JSON Orient", "choice", "records",
                choices=["records", "columns", "index", "values"],
            ))
            opts.append(ConversionOption(
                "indent", "Indent", "int", 2, min_val=0, max_val=8,
            ))
        return opts

    def convert(
        self,
        task: ConversionTask,
        progress_callback: Callable[[float], None] | None = None,
    ) -> Path:
        if progress_callback:
            progress_callback(0.0)

        in_fmt = task.input_path.suffix.lower().lstrip(".")
        out_fmt = task.output_format.lower()

        task.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Special case: JSON <-> YAML without pandas (preserves nested structures)
        if in_fmt == "json" and out_fmt == "yaml":
            self._json_to_yaml(task)
        elif in_fmt in ("yaml", "yml") and out_fmt == "json":
            self._yaml_to_json(task)
        else:
            self._convert_via_pandas(task, in_fmt, out_fmt)

        if progress_callback:
            progress_callback(1.0)

        return task.output_path

    def _json_to_yaml(self, task: ConversionTask):
        import yaml

        data = json.loads(task.input_path.read_text(encoding="utf-8"))
        with open(task.output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def _yaml_to_json(self, task: ConversionTask):
        import yaml

        with open(task.input_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        indent = task.options.get("indent", 2)
        with open(task.output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

    def _convert_via_pandas(self, task: ConversionTask, in_fmt: str, out_fmt: str):
        import pandas as pd

        # Read
        df = self._read_dataframe(task.input_path, in_fmt)

        # Write
        self._write_dataframe(df, task.output_path, out_fmt, task.options)

    def _read_dataframe(self, path: Path, fmt: str):
        import pandas as pd
        import yaml

        if fmt == "csv":
            return pd.read_csv(path)
        elif fmt == "json":
            return pd.read_json(path)
        elif fmt in ("xlsx", "xls"):
            return pd.read_excel(path)
        elif fmt == "xml":
            return pd.read_xml(path)
        elif fmt in ("yaml", "yml"):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                return pd.DataFrame([data])
            raise ConversionError("YAML data is not tabular")
        else:
            raise ConversionError(f"Cannot read format: {fmt}")

    def _write_dataframe(self, df, path: Path, fmt: str, options: dict):
        if fmt == "csv":
            sep = options.get("separator", ",")
            df.to_csv(path, index=False, sep=sep)
        elif fmt == "json":
            orient = options.get("orient", "records")
            indent = options.get("indent", 2)
            df.to_json(path, orient=orient, indent=indent, force_ascii=False)
        elif fmt == "xlsx":
            df.to_excel(path, index=False)
        elif fmt == "xml":
            df.to_xml(path, index=False)
        elif fmt == "yaml":
            import yaml
            data = df.to_dict(orient="records")
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ConversionError(f"Cannot write format: {fmt}")
