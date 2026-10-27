import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PyPdfError


class PDFProcessingError(Exception):
    """Raised when a PDF cannot be read or has no usable text."""


@dataclass
class Chunk:
    text: str
    page_number: int  # 1-based, matches what a human sees in the PDF viewer


def extract_pages(path: Path) -> list[tuple[int, str]]:
    """Returns a list of (page_number, text) for every page with text."""
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            raise PDFProcessingError("Password-protected PDFs are not supported")

        pages = []
        for number, page in enumerate(reader.pages, start=1):
            text = re.sub(r"\s+", " ", page.extract_text() or "").strip()
            if text:
                pages.append((number, text))
        return pages
    except PyPdfError as exc:
        raise PDFProcessingError("The file is not a valid PDF") from exc


def split_text(text: str, size: int = 1000, overlap: int = 200) -> list[str]:
    """Cuts text into overlapping pieces, preferring to break at spaces."""
    pieces = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            space = text.rfind(" ", start + size // 2, end)
            if space != -1:
                end = space
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return pieces


def process_pdf(path: Path) -> tuple[int, list[Chunk]]:
    """Returns (total_page_count, chunks)."""
    try:
        total_pages = len(PdfReader(str(path)).pages)
    except PyPdfError as exc:
        raise PDFProcessingError("The file is not a valid PDF") from exc

    chunks: list[Chunk] = []
    for page_number, text in extract_pages(path):
        for piece in split_text(text):
            chunks.append(Chunk(text=piece, page_number=page_number))

    if not chunks:
        raise PDFProcessingError(
            "No readable text found. Scanned PDFs (images) are not supported yet"
        )
    return total_pages, chunks