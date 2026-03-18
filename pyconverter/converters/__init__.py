from pyconverter.core.registry import ConverterRegistry
from pyconverter.converters.image import ImageConverter

_registered = False


def ensure_registered():
    global _registered
    if _registered:
        return
    _registered = True
    ConverterRegistry.register(ImageConverter())

    # Lazy-import optional converters to avoid import errors
    # if their dependencies are not installed
    try:
        from pyconverter.converters.document import DocumentConverter
        ConverterRegistry.register(DocumentConverter())
    except ImportError:
        pass

    try:
        from pyconverter.converters.data import DataConverter
        ConverterRegistry.register(DataConverter())
    except ImportError:
        pass

    try:
        from pyconverter.converters.audio import AudioConverter
        ConverterRegistry.register(AudioConverter())
    except ImportError:
        pass

    try:
        from pyconverter.converters.video import VideoConverter
        ConverterRegistry.register(VideoConverter())
    except ImportError:
        pass


ensure_registered()
