"""Inline SVG Material Design icons - no external dependencies."""

from PySide6.QtCore import QByteArray, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QPainter, QImage

_SVGS = {
    "convert": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M19 8l-4 4h3c0 3.31-2.69 6-6 6a5.87 5.87 0 01-2.8-.7l-1.46 1.46A7.93 7.93 0 0012 20c4.42 0 8-3.58 8-8h3l-4-4zM6 12c0-3.31 2.69-6 6-6 1.01 0 1.97.25 2.8.7l1.46-1.46A7.93 7.93 0 0012 4c-4.42 0-8 3.58-8 8H1l4 4 4-4H6z"/>
    </svg>""",
    "cancel": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
    </svg>""",
    "folder_open": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/>
    </svg>""",
    "browse": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M15.5 14h-.79l-.28-.27A6.47 6.47 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
    </svg>""",
    "preview": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
    </svg>""",
    "delete": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
    </svg>""",
    "clear": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M5 13h14v-2H5v2zm-2 4h14v-2H3v2zM7 7v2h14V7H7z"/>
    </svg>""",
    "close": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
    </svg>""",
    "add_file": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 14h-3v3h-2v-3H8v-2h3v-3h2v3h3v2zm-3-7V3.5L18.5 9H13z"/>
    </svg>""",
    "settings": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 00.12-.61l-1.92-3.32a.49.49 0 00-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 00-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.07.62-.07.94s.02.64.07.94l-2.03 1.58a.49.49 0 00-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
    </svg>""",
    "move_up": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z"/>
    </svg>""",
    "move_down": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6z"/>
    </svg>""",
    "cloud_upload": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="{color}" d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
    </svg>""",
}


def icon(name: str, color: str = "#cdd6f4", size: int = 24) -> QIcon:
    """Create a QIcon from an inline SVG template."""
    svg_str = _SVGS.get(name, "")
    if not svg_str:
        return QIcon()

    svg_data = svg_str.format(color=color).encode("utf-8")
    renderer = QSvgRenderer(QByteArray(svg_data))

    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()

    return QIcon(QPixmap.fromImage(image))


def icon_pixmap(name: str, color: str = "#cdd6f4", size: int = 24) -> QPixmap:
    """Create a QPixmap from an inline SVG template."""
    return icon(name, color, size).pixmap(QSize(size, size))
