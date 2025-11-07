# Mock Configuration Usage Examples

## Overview

Мок-данные теперь настраиваются через конфигурационный файл `mock_data.py` и могут использоваться как через обычные фикстуры, так и через параметризованные.

## 1. Использование обычных фикстур (backward compatible)

```python
def test_with_default_user(mock_user):
    """Использует дефолтного пользователя из конфига."""
    assert mock_user.id == 1
    assert mock_user.email == "test@example.com"

def test_with_second_user(mock_user_2):
    """Использует второго пользователя из конфига."""
    assert mock_user_2.id == 2
    assert mock_user_2.email == "user2@example.com"
```

## 2. Использование параметризованных фикстур

Параметризованные фикстуры автоматически запускают тест с каждым набором данных:

```python
def test_user_properties(mock_user_from_config):
    """Этот тест запустится 3 раза с разными пользователями (default, user_2, admin)."""
    assert mock_user_from_config.id > 0
    assert "@" in mock_user_from_config.email
    assert len(mock_user_from_config.user_name) > 0

def test_exam_properties(mock_exam_from_config):
    """Этот тест запустится 3 раза с разными экзаменами (default, exam_2, empty_exam)."""
    assert mock_exam_from_config.id > 0
    assert len(mock_exam_from_config.title) > 0

def test_cards_list(mock_cards_from_config):
    """Этот тест запустится 2 раза с разными наборами карточек (exam_1_cards, exam_2_cards)."""
    assert len(mock_cards_from_config) > 0
    for card in mock_cards_from_config:
        assert card.card_id > 0
```

## 3. Использование @pytest.mark.parametrize с конфигом

Вы также можете использовать `@pytest.mark.parametrize` напрямую с данными из конфига:

```python
import pytest
from tests.unit.mock_data import USERS

@pytest.mark.parametrize("user_key", ["default", "user_2", "admin"])
def test_specific_user(user_key):
    """Тест с конкретными пользователями."""
    from tests.unit.conftest import create_user_mock

    user = create_user_mock(USERS[user_key])
    assert user.id > 0

@pytest.mark.parametrize(
    "user_key,expected_id",
    [
        ("default", 1),
        ("user_2", 2),
        ("admin", 3),
    ]
)
def test_user_ids(user_key, expected_id):
    """Тест с проверкой конкретных значений."""
    from tests.unit.conftest import create_user_mock

    user = create_user_mock(USERS[user_key])
    assert user.id == expected_id
```

## 4. Создание кастомных моков в тестах

```python
def test_custom_user():
    """Создание кастомного пользователя для специфичного теста."""
    from tests.unit.conftest import create_user_mock

    custom_user = create_user_mock({
        "id": 999,
        "email": "custom@test.com",
        "user_name": "Custom User",
        "password_hash": "custom_hash",
    })

    assert custom_user.id == 999
    assert custom_user.email == "custom@test.com"
```

## 5. Indirect parametrization для более гибкого контроля

```python
@pytest.fixture
def custom_user(request):
    """Фикстура с indirect параметризацией."""
    from tests.unit.conftest import create_user_mock
    from tests.unit.mock_data import USERS

    return create_user_mock(USERS[request.param])

@pytest.mark.parametrize("custom_user", ["default", "admin"], indirect=True)
def test_with_indirect(custom_user):
    """Тест запустится только для default и admin пользователей."""
    assert custom_user.id in [1, 3]
```

## Преимущества этого подхода

1. **Централизованная конфигурация**: Все тестовые данные в одном месте (`mock_data.py`)
2. **Легко добавлять новые данные**: Просто добавляете новый ключ в словарь
3. **Параметризация**: Автоматический запуск тестов с разными наборами данных
4. **Обратная совместимость**: Старые тесты продолжают работать
5. **Гибкость**: Можно использовать и фикстуры, и прямое создание моков
6. **DRY**: Не дублируем код создания моков

## Добавление новых данных в конфиг

Чтобы добавить новый набор данных, просто отредактируйте `mock_data.py`:

```python
USERS = {
    "default": {...},
    "new_user": {  # Добавляем нового пользователя
        "id": 10,
        "email": "newuser@example.com",
        "user_name": "New User",
        "password_hash": "new_hash",
    },
}
```

Затем обновите параметры фикстуры в `conftest.py`:

```python
@pytest.fixture(params=["default", "user_2", "admin", "new_user"])  # Добавляем в params
def user_config(request):
    return USERS[request.param]
```