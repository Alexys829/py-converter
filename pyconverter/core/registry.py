from __future__ import annotations

from pyconverter.core.base_converter import BaseConverter
from pyconverter.core.exceptions import ConverterNotFoundError


class ConverterRegistry:
    _converters: list[BaseConverter] = []

    @classmethod
    def register(cls, converter: BaseConverter) -> None:
        cls._converters.append(converter)

    @classmethod
    def find_converter(cls, input_format: str, output_format: str) -> BaseConverter:
        fmt_in = input_format.lower().lstrip(".")
        fmt_out = output_format.lower().lstrip(".")
        for converter in cls._converters:
            if converter.can_convert(fmt_in, fmt_out):
                return converter
        raise ConverterNotFoundError(
            f"No converter found for {fmt_in} -> {fmt_out}"
        )

    @classmethod
    def get_output_formats(cls, input_format: str) -> list[str]:
        fmt_in = input_format.lower().lstrip(".")
        formats: set[str] = set()
        for converter in cls._converters:
            if fmt_in in converter.supported_input_formats():
                formats.update(converter.supported_output_formats())
        return sorted(formats)

    @classmethod
    def get_all_input_formats(cls) -> list[str]:
        formats: set[str] = set()
        for converter in cls._converters:
            formats.update(converter.supported_input_formats())
        return sorted(formats)

    @classmethod
    def list_converters(cls) -> list[BaseConverter]:
        return list(cls._converters)

    @classmethod
    def clear(cls) -> None:
        cls._converters.clear()
