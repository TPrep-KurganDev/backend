
# Инструкция по запуску проекта FastAPI с PostgreSQL

Эта инструкция поможет другим разработчикам быстро поднять проект, создать базу данных и настроить миграции.

---

## 1. Создание `.env` файла

Создаёте файл '.env' и пишите в него такое

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/[имя бд]
SECRET_KEY= [любая длинная сгенерированная строка]
ALGORITHM= [по дефолту HS256]
ACCESS_TOKEN_EXPIRE_MINUTES= [по дефолту 60]
```

---

## 2. Инициализация базы данных

В корне проекта выполните команду:

```bash
python init_db.py
```

Что произойдет:

1. Скрипт проверит наличие базы данных, указанной в DATABASE_URl на локальном PostgreSQL сервере.  
2. Если базы нет — создаст её автоматически.

---

## 3. Настройка Alembic

Alembic используется для управления миграциями базы данных.

### 3.1 Проверка конфигурации

 В файле `alembic.ini` ищем строку:
```bash
  sqlalchemy.url = [Вставить DATABASE_URl]
```
- В файле `migrations/env.py` поменять код.
- Ищем такой блок
```python
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

config = context.config
fileConfig(config.config_file_name)
target_metadata = None
```
Заменяем его на:

```python
import os
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context
from logging.config import fileConfig
from infrastructure.models import *
from infrastructure.user.user import *
from infrastructure.exam.exam import *

load_dotenv()

config = context.config
fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

target_metadata = Base.metadata
```

### 3.2 Создание новой миграции

После изменений в моделях выполняем:

```bash
alembic revision --autogenerate -m "init"
```

- Alembic сравнит текущие модели с базой и создаст SQL скрипт в `migrations/versions/`.

### 3.3 Применение миграций

Чтобы обновить базу до последней версии:

```bash
alembic upgrade head
```


### 3.4 Откат миграции (при необходимости)

```bash
alembic downgrade -1
```
### 3.5 ГДЕ ПОСМОТРЕТЬ БД

В pgAdmine или в консоли

---

## 4. Запуск FastAPI

После создания базы и применения миграций можно запускать сервер:

```bash
uvicorn app.main:app --reload
```

- Сервер будет доступен по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000) 
- Можно написать [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) и увидеть статус

---
