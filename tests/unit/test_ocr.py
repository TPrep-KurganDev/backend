from __future__ import annotations

from pathlib import Path

import pytest

from tprep.infrastructure.ocr import extract_text_from_image


def test_extract_text_from_image_example_png_integration() -> None:
    try:
        import easyocr
    except ImportError:
        pytest.skip("easyocr is not installed")

    project_root = Path(__file__).resolve().parents[2]
    example_path = project_root / "images" / "example.png"
    if not example_path.exists():
        pytest.skip("images/example.png is missing")

    lines = extract_text_from_image("example.png")
    assert lines == ["Гении не рождаются"] #сюда ввести тексты по строкам, который на картинке
    assert isinstance(lines, list)

