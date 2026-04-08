# from __future__ import annotations
#
# import os
# from pathlib import Path
#
# import pytest
# from dotenv import load_dotenv
#
# from tprep.infrastructure.ocr import (
#     OcrParseError,
#     cards_from_image,
#     extract_text_from_image,
#     parse_cards_json_response,
# )
#
# load_dotenv()
#
# def test_parse_cards_json_response_plain() -> None:
#     raw = '{"cards":[{"question":"Q1","answer":"A1"},{"question":"Q2","answer":"A2"}]}'
#     assert parse_cards_json_response(raw) == [("Q1", "A1"), ("Q2", "A2")]
#
#
# def test_parse_cards_json_response_strips_fence() -> None:
#     raw = '```json\n{"cards":[{"question":"x","answer":"y"}]}\n```'
#     assert parse_cards_json_response(raw) == [("x", "y")]
#
#
# def test_parse_cards_json_response_skips_empty_pairs() -> None:
#     raw = '{"cards":[{"question":"","answer":"a"},{"question":"q","answer":""},{"question":"ok","answer":"ok"}]}'
#     assert parse_cards_json_response(raw) == [("ok", "ok")]
#
#
# def test_parse_cards_json_response_invalid_raises() -> None:
#     with pytest.raises(OcrParseError):
#         parse_cards_json_response("not json")
#
#
# def test_extract_text_from_image_example_jpg_openrouter() -> None:
#     """Требует OPENROUTER_API_KEY и сеть; проверяет реальный вызов OpenRouter."""
#     if not os.getenv("OPENROUTER_API_KEY"):
#         pytest.skip("OPENROUTER_API_KEY is not set")
#
#     project_root = Path(__file__).resolve().parents[2]
#     example_path = project_root / "images" / "example.jpg"
#     if not example_path.is_file():
#         pytest.skip("images/example.jpg is missing")
#
#     lines = extract_text_from_image("example.jpg")
#     for line in lines:
#         print(line)
#     assert isinstance(lines, list)
#     assert any(len(line.strip()) > 0 for line in lines)
#
#
# def test_cards_from_image_card_example_jpg_openrouter() -> None:
#     """Требует OPENROUTER_API_KEY, сеть и images/card_example.jpg; парсит картинку в пары карточек."""
#     if not os.getenv("OPENROUTER_API_KEY"):
#         pytest.skip("OPENROUTER_API_KEY is not set")
#
#     project_root = Path(__file__).resolve().parents[2]
#     card_image = project_root / "images" / "card_example.jpg"
#     if not card_image.is_file():
#         pytest.skip("images/card_example.jpg is missing")
#
#     pairs = cards_from_image("card_example.jpg")
#
#     assert isinstance(pairs, list)
#     assert len(pairs) >= 1, "модель должна вернуть хотя бы одну пару question/answer"
#     for question, answer in pairs:
#         print(question, answer)
#         assert isinstance(question, str) and isinstance(answer, str)
#         assert question.strip(), "question не должен быть пустым"
#         assert answer.strip(), "answer не должен быть пустым"
