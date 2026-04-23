import json
import os
import base64
import re
import requests
from pathlib import Path
from typing import Any, Optional
from PIL import Image
from io import BytesIO

from dotenv import load_dotenv

load_dotenv()

_HEADERS = {
    "HTTP-Referer": "https://tprep.local",
    "X-Title": "Backend OCR Service",
}

_CARD_FIELD_MAX_LEN = 500

CARD_STRUCTURE_PROMPT = (
    "Ты читаешь текст с изображения и формируешь тренировочные карточки в формате вопрос–ответ "
    "Правила:\n"
    "1. Верни ТОЛЬКО один JSON-объект без пояснений, без markdown-обёрток.\n"
    '2. Формат: {"cards":[{"question":"...","answer":"..."}, ...]}\n'
    "3. Если на изображении явно видны пары (термин/определение, вопрос/ответ, столбцы) — "
    "сохрани их как отдельные элементы cards.\n"
    "4. Если текст сплошной — разбей логически на карточки (один факт или тема на карточку).\n"
    "5. Поля question и answer — непустые строки, каждая не длиннее "
    f"{_CARD_FIELD_MAX_LEN} символов; при необходимости сократи.\n"
    '6. Если распознать пары нельзя — верни {"cards":[]}.\n'
)


class OcrConfigurationError(Exception):
    """Нет ключа OpenRouter или иная ошибка конфигурации OCR."""


class OcrParseError(ValueError):
    """Ответ модели не удалось разобрать в список карточек."""


def _image_to_base64(image_path: str | Path, max_size: int = 1024) -> str:
    """Сжимает изображение (если нужно) и кодирует в base64"""
    img = Image.open(str(image_path)).convert("RGB")
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _images_base_dir() -> Path:
    return (Path(__file__).resolve().parents[2] / "images").resolve()


def _resolve_image_path(image_name: str) -> Path:
    """Путь к файлу в каталоге images/ проекта; защита от выхода за пределы каталога."""
    base = _images_base_dir()
    candidate = Path(image_name)
    if candidate.is_absolute():
        raise ValueError("Invalid image path")
    resolved = (base / candidate).resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise ValueError("Invalid image path") from exc
    if not resolved.is_file():
        raise FileNotFoundError(str(resolved))
    return resolved


def extract_text_from_image(
    image_name: str,
    *,
    api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
) -> list[str]:
    """Распознаёт текст с изображения через OpenRouter; `image_name` — имя или путь относительно images/."""
    path = _resolve_image_path(image_name)
    resolved_model = os.getenv("OCR_DEFAULT_MODEL")
    text = recognize_handwriting(path, api_key=api_key, model=resolved_model)
    return text.splitlines()


def _strip_json_fence(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, count=1, flags=re.IGNORECASE)
        text = re.sub(r"\s*```\s*$", "", text, count=1)
    return text.strip()


def _clip_field(value: str) -> str:
    s = value.strip()
    if len(s) > _CARD_FIELD_MAX_LEN:
        return s[:_CARD_FIELD_MAX_LEN]
    return s


def parse_cards_json_response(raw: str) -> list[tuple[str, str]]:
    """Парсит JSON вида {\"cards\":[{\"question\":\"...\",\"answer\":\"...\"}]} в пары для create_card_by_list."""
    cleaned = _strip_json_fence(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise OcrParseError(f"Невалидный JSON от модели: {exc}") from exc

    if not isinstance(data, dict):
        raise OcrParseError("Ожидался JSON-объект с ключом cards")
    cards_raw = data.get("cards")
    if cards_raw is None:
        raise OcrParseError("В ответе нет поля cards")
    if not isinstance(cards_raw, list):
        raise OcrParseError("Поле cards должно быть массивом")

    pairs: list[tuple[str, str]] = []
    for i, item in enumerate(cards_raw):
        if not isinstance(item, dict):
            raise OcrParseError(f"Элемент cards[{i}] должен быть объектом")
        q = item.get("question")
        a = item.get("answer")
        if q is None or a is None:
            raise OcrParseError(f"В cards[{i}] нужны поля question и answer")
        question = _clip_field(str(q))
        answer = _clip_field(str(a))
        if not question or not answer:
            continue
        pairs.append((question, answer))

    return pairs


def cards_from_image(
    image_name: str,
    *,
    api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY"),
    model: Optional[str] = os.getenv("OCR_DEFAULT_MODEL"),
) -> list[tuple[str, str]]:
    """Распознаёт изображение и возвращает пары (question, answer) для ExamRepo.create_card_by_list."""
    path = _resolve_image_path(image_name)
    resolved_model: str = model or os.getenv("OCR_DEFAULT_MODEL")
    raw = recognize_handwriting(
        path,
        api_key=api_key,
        model=resolved_model,
        prompt=CARD_STRUCTURE_PROMPT,
        max_tokens=2048,
    )
    return parse_cards_json_response(raw)


def recognize_handwriting(
    image_path: str | Path,
    api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY"),
    model: str = os.getenv("OCR_DEFAULT_MODEL"),
    prompt: Optional[str] = None,
    timeout: int = 60,
    max_tokens: int = 2048,
) -> str:
    """Отправляет изображение на OCR через OpenRouter API"""
    api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise OcrConfigurationError(
            "Не указан API_KEY. Передайте параметром `api_key=` "
            "или установите переменную OPENROUTER_API_KEY в .env"
        )

    print(api_key)

    prompt = prompt or (
        "Ты специалист по распознаванию рукописного текста на русском языке. "
        "Транскрибируй весь текст с изображения, сохраняя структуру, пунктуацию и регистр. "
        "Неразборчивые слова помечай как [нрзб]. "
        "Выводи ТОЛЬКО распознанный текст, без пояснений."
    )

    img_b64 = _image_to_base64(image_path)

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={**_HEADERS, "Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
                        },
                    ],
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.1,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload: Any = response.json()
    content = payload["choices"][0]["message"]["content"]
    if not isinstance(content, str):
        raise RuntimeError("Неожиданный формат ответа OpenRouter (content не строка)")
    return content.strip()
