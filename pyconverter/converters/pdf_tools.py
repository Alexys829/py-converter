from pathlib import Path
from typing import Callable
import fitz

from pyconverter.core.base_converter import BaseConverter, ConversionOption, ConversionTask
from pyconverter.core.exceptions import ConversionError


def merge_pdfs(input_paths: list[Path], output_path: Path, progress_callback=None) -> Path:
    """Merge multiple PDFs into one."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = fitz.open()
    total = len(input_paths)
    for i, path in enumerate(input_paths):
        doc = fitz.open(str(path))
        result.insert_pdf(doc)
        doc.close()
        if progress_callback:
            progress_callback((i + 1) / total)
    result.save(str(output_path))
    result.close()
    return output_path


def split_pdf(input_path: Path, output_dir: Path, progress_callback=None) -> list[Path]:
    """Split a PDF into individual pages."""
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(input_path))
    total = len(doc)
    results = []
    for i in range(total):
        out = fitz.open()
        out.insert_pdf(doc, from_page=i, to_page=i)
        out_path = output_dir / f"{input_path.stem}_page_{i+1}.pdf"
        out.save(str(out_path))
        out.close()
        results.append(out_path)
        if progress_callback:
            progress_callback((i + 1) / total)
    doc.close()
    return results


def extract_pages(input_path: Path, output_path: Path, pages: list[int], progress_callback=None) -> Path:
    """Extract specific pages (0-indexed) from a PDF."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(input_path))
    result = fitz.open()
    total = len(pages)
    for i, page_num in enumerate(pages):
        if 0 <= page_num < len(doc):
            result.insert_pdf(doc, from_page=page_num, to_page=page_num)
        if progress_callback:
            progress_callback((i + 1) / total)
    result.save(str(output_path))
    result.close()
    doc.close()
    return output_path


def insert_pages(target_path: Path, source_path: Path, output_path: Path,
                 insert_after: int = -1, source_pages: list[int] | None = None) -> Path:
    """Insert pages from source PDF into target PDF at a specific position.
    insert_after: -1 means at the beginning, 0 after first page, etc.
    source_pages: list of 0-indexed page numbers to insert, None means all pages.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    target = fitz.open(str(target_path))
    source = fitz.open(str(source_path))

    if source_pages is None:
        source_pages = list(range(len(source)))

    # We need to build a new doc: pages before insert point, then source pages, then remaining
    result = fitz.open()

    # Pages before insert point
    if insert_after >= 0:
        result.insert_pdf(target, from_page=0, to_page=min(insert_after, len(target) - 1))

    # Insert source pages
    for pg in source_pages:
        if 0 <= pg < len(source):
            result.insert_pdf(source, from_page=pg, to_page=pg)

    # Remaining pages from target
    start = insert_after + 1 if insert_after >= 0 else 0
    if start < len(target):
        result.insert_pdf(target, from_page=start, to_page=len(target) - 1)

    result.save(str(output_path))
    result.close()
    target.close()
    source.close()
    return output_path


def remove_pages(input_path: Path, output_path: Path, pages_to_remove: list[int]) -> Path:
    """Remove specific pages (0-indexed) from a PDF."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(input_path))
    pages_to_keep = [i for i in range(len(doc)) if i not in pages_to_remove]
    result = fitz.open()
    for pg in pages_to_keep:
        result.insert_pdf(doc, from_page=pg, to_page=pg)
    result.save(str(output_path))
    result.close()
    doc.close()
    return output_path


def reorder_pages(input_path: Path, output_path: Path, new_order: list[int]) -> Path:
    """Reorder pages according to new_order (list of 0-indexed page numbers)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(input_path))
    result = fitz.open()
    for pg in new_order:
        if 0 <= pg < len(doc):
            result.insert_pdf(doc, from_page=pg, to_page=pg)
    result.save(str(output_path))
    result.close()
    doc.close()
    return output_path


def add_watermark(input_path: Path, output_path: Path, text: str,
                  opacity: float = 0.3, font_size: float = 50,
                  rotation: float = 45) -> Path:
    """Add a text watermark to every page of a PDF."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(input_path))
    for page in doc:
        rect = page.rect
        # Center of page
        center_x = rect.width / 2
        center_y = rect.height / 2
        # Insert text with rotation
        tw = fitz.TextWriter(page.rect)
        font = fitz.Font("helv")
        text_width = font.text_length(text, fontsize=font_size)
        x = center_x - text_width / 2
        y = center_y
        tw.append((x, y), text, font=font, fontsize=font_size)
        tw.write_text(page, opacity=opacity, morph=(fitz.Point(center_x, center_y), fitz.Matrix(rotation)))
    doc.save(str(output_path))
    doc.close()
    return output_path
