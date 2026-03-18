"""Generate app_icon.ico from SVG for PyInstaller on Windows.
Run: python scripts/generate_ico.py
"""
from pathlib import Path
from PIL import Image, ImageDraw

ICON_DIR = Path(__file__).parent.parent / "pyconverter" / "resources" / "icons"
OUTPUT = ICON_DIR / "app_icon.ico"

SIZES = [16, 32, 48, 64, 128, 256]


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    p = size / 128  # scale factor

    # Background circle
    draw.ellipse([4 * p, 4 * p, 124 * p, 124 * p], fill=(30, 30, 46, 255))

    # Back document (blue)
    draw.rounded_rectangle(
        [28 * p, 20 * p, 72 * p, 100 * p],
        radius=4 * p, fill=(137, 180, 250, 255),
    )

    # Front document (green)
    draw.rounded_rectangle(
        [56 * p, 28 * p, 100 * p, 108 * p],
        radius=4 * p, fill=(166, 227, 161, 255),
    )

    # Arrow
    arrow_y = 64 * p
    draw.polygon(
        [(40 * p, arrow_y - 8 * p), (40 * p, arrow_y + 8 * p), (54 * p, arrow_y)],
        fill=(205, 214, 244, 255),
    )

    return img


def main():
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    images = [draw_icon(s) for s in SIZES]
    images[0].save(str(OUTPUT), format="ICO", sizes=[(s, s) for s in SIZES],
                   append_images=images[1:])
    print(f"Generated: {OUTPUT}")


if __name__ == "__main__":
    main()
