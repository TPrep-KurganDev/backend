import pytest
import os
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from tprep.infrastructure.models import Base
from tprep.infrastructure.user.user import User
from tprep.infrastructure.exam.exam import Exam, Card
from tprep.infrastructure.statistic.statistic import Statistic


# URL для тестовой БД (можно переопределить через переменную окружения)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://test_user:test_password@localhost:5433/test_db"
)


@pytest.fixture
def mock_stat_repo():
    with patch("tprep.domain.exam_session.StatRepo.inc_mistakes") as mock:
        yield mock


@pytest.fixture(autouse=True)
def clear_session_factory():
    from tprep.domain.services.session_factory import SessionFactory

    SessionFactory.session_ids = {}
    yield
    SessionFactory.session_ids = {}


@pytest.fixture(scope="session")
def db_engine():
    """
    Создает engine для подключения к тестовой БД.
    Engine создается один раз для всей сессии тестов.
    """
    engine = create_engine(TEST_DATABASE_URL, echo=False)

    # Создаем все таблицы один раз перед всеми тестами
    Base.metadata.create_all(bind=engine)

    yield engine

    # Удаляем все таблицы после всех тестов
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(db_engine) -> Session:
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.rollback()  # Откатываем незакоммиченные изменения
        db.close()

        # Очищаем все таблицы после теста
        with db_engine.connect() as connection:
            trans = connection.begin()
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(table.delete())
            trans.commit()


@pytest.fixture
def populate_db(test_db: Session):
    """
    Фабрика для заполнения тестовой БД данными.

    Использование:
        populate_db(users=[
            {"id": 1, "email": "test@example.com", "user_name": "Test", "password_hash": "hash"}
        ])
    """

    def _populate(users=None, exams=None, cards=None, statistics=None):
        # Добавляем пользователей
        if users:
            for user_data in users:
                user = User(**user_data)
                test_db.add(user)

        # Добавляем экзамены
        if exams:
            for exam_data in exams:
                exam = Exam(**exam_data)
                test_db.add(exam)

        # Добавляем карточки
        if cards:
            for card_data in cards:
                card = Card(**card_data)
                test_db.add(card)

        # Добавляем статистику
        if statistics:
            for stat_data in statistics:
                stat = Statistic(**stat_data)
                test_db.add(stat)

        # Фиксируем изменения
        test_db.commit()

    return _populate
