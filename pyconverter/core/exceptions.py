class ConversionError(Exception):
    """Raised when a conversion fails."""


class UnsupportedFormatError(ConversionError):
    """Raised when the input or output format is not supported."""


class ConverterNotFoundError(ConversionError):
    """Raised when no converter is found for a format pair."""
