import argparse
import sys
from pathlib import Path

from pyconverter.core.registry import ConverterRegistry
from pyconverter.core.base_converter import ConversionTask
from pyconverter.core.format_detector import detect_format


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pyconverter",
        description="Universal PyConverter",
    )
    sub = parser.add_subparsers(dest="command")

    # convert
    conv = sub.add_parser("convert", help="Convert a single file")
    conv.add_argument("input", help="Input file path")
    conv.add_argument("-o", "--output", help="Output file path")
    conv.add_argument("-f", "--format", required=True, help="Target format (e.g. png, pdf)")
    conv.add_argument(
        "--option", nargs=2, action="append", metavar=("KEY", "VALUE"),
        help="Converter option (e.g. --option quality 80)",
    )

    # batch
    batch = sub.add_parser("batch", help="Batch convert files")
    batch.add_argument("inputs", nargs="+", help="Input files or directories")
    batch.add_argument("-f", "--format", required=True, help="Target format")
    batch.add_argument("-d", "--output-dir", default=".", help="Output directory")
    batch.add_argument("-r", "--recursive", action="store_true",
                       help="Recursively process directories")
    batch.add_argument(
        "--option", nargs=2, action="append", metavar=("KEY", "VALUE"),
        help="Converter option",
    )

    # formats
    sub.add_parser("formats", help="List all supported format conversions")

    return parser


def _parse_options(raw_options: list[list[str]] | None) -> dict:
    if not raw_options:
        return {}
    opts = {}
    for key, value in raw_options:
        try:
            opts[key] = int(value)
        except ValueError:
            try:
                opts[key] = float(value)
            except ValueError:
                opts[key] = value
    return opts


def _make_output_path(input_path: Path, output_format: str, output_dir: Path | None = None) -> Path:
    stem = input_path.stem
    out_name = f"{stem}.{output_format}"
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / out_name
    return input_path.parent / out_name


def cmd_convert(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    input_format = detect_format(input_path)
    if not input_format:
        print(f"Error: cannot detect format of {input_path}", file=sys.stderr)
        sys.exit(1)

    output_format = args.format.lower().lstrip(".")
    options = _parse_options(args.option)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = _make_output_path(input_path, output_format)

    converter = ConverterRegistry.find_converter(input_format, output_format)
    task = ConversionTask(
        input_path=input_path,
        output_path=output_path,
        output_format=output_format,
        options=options,
    )
    result = converter.convert(task)
    print(f"Converted: {input_path} -> {result}")


def _collect_files(inputs: list[str], recursive: bool) -> list[Path]:
    """Collect files from paths and directories."""
    files = []
    for item in inputs:
        path = Path(item)
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            if recursive:
                files.extend(p for p in path.rglob("*") if p.is_file())
            else:
                files.extend(p for p in path.iterdir() if p.is_file())
        else:
            print(f"Skipping (not found): {path}", file=sys.stderr)
    return files


def cmd_batch(args: argparse.Namespace) -> None:
    output_format = args.format.lower().lstrip(".")
    output_dir = Path(args.output_dir)
    options = _parse_options(args.option)
    recursive = getattr(args, "recursive", False)

    files = _collect_files(args.inputs, recursive)
    if not files:
        print("No files found.", file=sys.stderr)
        return

    converted = 0
    failed = 0
    for input_path in files:
        input_format = detect_format(input_path)
        if not input_format:
            print(f"Skipping (unknown format): {input_path}", file=sys.stderr)
            continue

        try:
            converter = ConverterRegistry.find_converter(input_format, output_format)
        except Exception as e:
            print(f"Skipping {input_path}: {e}", file=sys.stderr)
            continue

        output_path = _make_output_path(input_path, output_format, output_dir)
        task = ConversionTask(
            input_path=input_path,
            output_path=output_path,
            output_format=output_format,
            options=options,
        )
        try:
            result = converter.convert(task)
            print(f"Converted: {input_path} -> {result}")
            converted += 1
        except Exception as e:
            print(f"Failed {input_path}: {e}", file=sys.stderr)
            failed += 1

    print(f"\nDone: {converted} converted, {failed} failed, {len(files)} total")


def cmd_formats(args: argparse.Namespace) -> None:
    converters = ConverterRegistry.list_converters()
    if not converters:
        print("No converters registered.")
        return

    for conv in converters:
        print(f"\n{conv.name()}")
        print(f"  Input:  {', '.join(conv.supported_input_formats())}")
        print(f"  Output: {', '.join(conv.supported_output_formats())}")


def run_cli() -> None:
    # Ensure converters are registered
    import pyconverter.converters  # noqa: F401

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "convert":
        cmd_convert(args)
    elif args.command == "batch":
        cmd_batch(args)
    elif args.command == "formats":
        cmd_formats(args)
    else:
        parser.print_help()
