from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException, status


_ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _images_dir() -> Path:
    return _project_root() / "images"


def _safe_image_path(image_name: str) -> Path:
    images_dir = _images_dir()
    if not images_dir.exists() or not images_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Images directory is missing",
        )

    candidate = (images_dir / image_name).resolve()
    if images_dir.resolve() not in candidate.parents and candidate != images_dir.resolve():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image path",
        )

    if candidate.suffix.lower() not in _ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported image extension",
        )

    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )

    return candidate


@lru_cache(maxsize=1)
def _get_reader() -> "easyocr.Reader":
    try:
        import easyocr
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="EasyOCR is not installed",
        ) from e

    return easyocr.Reader(["en", "ru"])


def extract_text_from_image(
    image_name: str,
) -> list[str]:
    image_path = _safe_image_path(image_name)
    reader = _get_reader()

    result = reader.readtext(str(image_path), detail=1, paragraph=False)
    lines: list[str] = []
    for item in result:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            text = str(item[1]).strip()
            if text:
                lines.append(text)

    return lines

