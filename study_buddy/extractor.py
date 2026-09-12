"""Extracts plain text from PDF and image files."""
from pathlib import Path


import pdfplumber
import pytesseract
from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif"}


def extract_text(file_path: str) -> str:
    """Extract text from a PDF or image file. Raises ValueError for unsupported types."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_from_pdf(path)
    if suffix in IMAGE_EXTENSIONS:
        return _extract_from_image(path)
    if suffix == ".txt":
        return path.read_text(encoding="utf-8")

    raise ValueError(f"Unsupported file type: {suffix}")


def _extract_from_pdf(path: Path) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_from_image(path: Path) -> str:
    with Image.open(path) as img:
        return pytesseract.image_to_string(img)
