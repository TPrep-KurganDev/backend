import uuid
import pytest

from tprep.infrastructure import User, Exam, Card
from tprep.infrastructure.statistic.stat_repo import StatRepo
from tprep.infrastructure.statistic.statistic import Statistic


class TestStatRepoIncMistakes:
    def test_inc_mistakes_increments_existing_statistic(self, test_db, populate_db):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())

        # Создаем данные без явных ID для карт и статистики
        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": "user1@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": "Exam", "creator_id": user_id}],
            cards=[
                {
                    "exam_id": exam_id,
                    "question": "Q?",
                    "answer": "A",
                    "number": 1,
                }
            ],
        )

        # Получаем реальный ID созданной карты
        card = test_db.query(Card).filter(Card.exam_id == uuid.UUID(exam_id)).first()
        card_id = card.card_id

        # Создаем статистику вручную с реальными ID
        stat = Statistic(
            user_id=uuid.UUID(user_id),
            card_id=card_id,
            exam_id=uuid.UUID(exam_id),
            mistakes_count=5
        )
        test_db.add(stat)
        test_db.commit()

        StatRepo.inc_mistakes(user_id, card_id, test_db)

        # Проверяем что счетчик увеличился
        updated_stat = (
            test_db.query(Statistic)
            .filter(Statistic.user_id == uuid.UUID(user_id), Statistic.card_id == card_id)
            .first()
        )
        assert updated_stat is not None
        assert updated_stat.mistakes_count == 6

    def test_inc_mistakes_creates_new_statistic_when_not_exists(
            self, test_db, populate_db
    ):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": "user1@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": "Exam", "creator_id": user_id}],
            cards=[
                {
                    "exam_id": exam_id,
                    "question": "Q?",
                    "answer": "A",
                    "number": 1,
                }
            ],
        )

        card = test_db.query(Card).filter(Card.exam_id == uuid.UUID(exam_id)).first()
        card_id = card.card_id

        StatRepo.inc_mistakes(user_id, card_id, test_db)

        # Проверяем что статистика создана
        stat = (
            test_db.query(Statistic)
            .filter(Statistic.user_id == uuid.UUID(user_id), Statistic.card_id == card_id)
            .first()
        )
        assert stat is not None
        assert stat.mistakes_count == 1

    def test_inc_mistakes_increments_multiple_times(self, test_db, populate_db):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": "user1@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": "Exam", "creator_id": user_id}],
            cards=[
                {
                    "exam_id": exam_id,
                    "question": "Q?",
                    "answer": "A",
                    "number": 1,
                }
            ],
        )

        card = test_db.query(Card).filter(Card.exam_id == uuid.UUID(exam_id)).first()
        card_id = card.card_id

        # Создаем начальную статистику
        stat = Statistic(
            user_id=uuid.UUID(user_id),
            card_id=card_id,
            exam_id=uuid.UUID(exam_id),
            mistakes_count=5
        )
        test_db.add(stat)
        test_db.commit()

        # Увеличиваем счетчик 3 раза
        for _ in range(3):
            StatRepo.inc_mistakes(user_id, card_id, test_db)

        # Проверяем результат
        updated_stat = (
            test_db.query(Statistic)
            .filter(Statistic.user_id == uuid.UUID(user_id), Statistic.card_id == card_id)
            .first()
        )
        assert updated_stat is not None
        assert updated_stat.mistakes_count == 8

    def test_inc_mistakes_different_users_separate_statistics(
            self, test_db, populate_db
    ):
        user_id_1 = str(uuid.uuid4())
        user_id_2 = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())

        populate_db(
            users=[
                {
                    "id": user_id_1,
                    "email": "user1@example.com",
                    "user_name": "User1",
                    "password_hash": "hash",
                },
                {
                    "id": user_id_2,
                    "email": "user2@example.com",
                    "user_name": "User2",
                    "password_hash": "hash",
                },
            ],
            exams=[{"id": exam_id, "title": "Exam", "creator_id": user_id_1}],
            cards=[
                {
                    "exam_id": exam_id,
                    "question": "Q?",
                    "answer": "A",
                    "number": 1,
                }
            ],
        )

        card = test_db.query(Card).filter(Card.exam_id == uuid.UUID(exam_id)).first()
        card_id = card.card_id

        # Создаем статистику для обоих пользователей
        stat1 = Statistic(
            user_id=uuid.UUID(user_id_1),
            card_id=card_id,
            exam_id=uuid.UUID(exam_id),
            mistakes_count=5
        )
        stat2 = Statistic(
            user_id=uuid.UUID(user_id_2),
            card_id=card_id,
            exam_id=uuid.UUID(exam_id),
            mistakes_count=3
        )
        test_db.add_all([stat1, stat2])
        test_db.commit()

        # Увеличиваем счетчик только для пользователя 1
        StatRepo.inc_mistakes(user_id_1, card_id, test_db)

        # Проверяем что изменилась только статистика пользователя 1
        updated_stat1 = (
            test_db.query(Statistic)
            .filter(Statistic.user_id == uuid.UUID(user_id_1), Statistic.card_id == card_id)
            .first()
        )
        updated_stat2 = (
            test_db.query(Statistic)
            .filter(Statistic.user_id == uuid.UUID(user_id_2), Statistic.card_id == card_id)
            .first()
        )

        assert updated_stat1.mistakes_count == 6
        assert updated_stat2.mistakes_count == 3  # Не изменилось