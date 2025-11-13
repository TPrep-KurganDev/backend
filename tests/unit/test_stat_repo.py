from tprep.infrastructure.statistic.stat_repo import StatRepo
from tprep.infrastructure.statistic.statistic import Statistic


class TestStatRepoIncMistakes:
    def test_inc_mistakes_increments_existing_statistic(self, test_db, populate_db):
        # Создаем пользователя, экзамен, карточку и статистику
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "user1@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q?",
                    "answer": "A",
                    "number": 1,
                }
            ],
            statistics=[
                {"id": 1, "user_id": 1, "card_id": 1, "exam_id": 1, "mistakes_count": 5}
            ],
        )

        StatRepo.inc_mistakes(1, 1, test_db)

        # Проверяем что счетчик увеличился
        stat = (
            test_db.query(Statistic)
            .filter(Statistic.user_id == 1, Statistic.card_id == 1)
            .first()
        )
        assert stat is not None
        assert stat.mistakes_count == 6

    def test_inc_mistakes_creates_new_statistic_when_not_exists(
        self, test_db, populate_db
    ):
        # Создаем пользователя, экзамен и карточку (без статистики)
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "user1@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 10,
                    "exam_id": 1,
                    "question": "Q?",
                    "answer": "A",
                    "number": 1,
                }
            ],
        )

        StatRepo.inc_mistakes(1, 10, test_db)

        # Проверяем что статистика создана
        stat = (
            test_db.query(Statistic)
            .filter(Statistic.user_id == 1, Statistic.card_id == 10)
            .first()
        )
        assert stat is not None
        assert stat.mistakes_count == 1

    def test_inc_mistakes_increments_multiple_times(self, test_db, populate_db):
        # Создаем начальные данные
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "user1@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q?",
                    "answer": "A",
                    "number": 1,
                }
            ],
            statistics=[
                {"id": 1, "user_id": 1, "card_id": 1, "exam_id": 1, "mistakes_count": 5}
            ],
        )

        # Увеличиваем счетчик 3 раза
        for _ in range(3):
            StatRepo.inc_mistakes(1, 1, test_db)

        # Проверяем результат
        stat = (
            test_db.query(Statistic)
            .filter(Statistic.user_id == 1, Statistic.card_id == 1)
            .first()
        )
        assert stat is not None
        assert stat.mistakes_count == 8

    def test_inc_mistakes_different_users_separate_statistics(
        self, test_db, populate_db
    ):
        # Создаем двух пользователей и общую карточку
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "user1@example.com",
                    "user_name": "User1",
                    "password_hash": "hash",
                },
                {
                    "id": 2,
                    "email": "user2@example.com",
                    "user_name": "User2",
                    "password_hash": "hash",
                },
            ],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q?",
                    "answer": "A",
                    "number": 1,
                }
            ],
            statistics=[
                {
                    "id": 1,
                    "user_id": 1,
                    "card_id": 1,
                    "exam_id": 1,
                    "mistakes_count": 5,
                },
                {
                    "id": 2,
                    "user_id": 2,
                    "card_id": 1,
                    "exam_id": 1,
                    "mistakes_count": 3,
                },
            ],
        )

        # Увеличиваем счетчик для пользователя 1
        StatRepo.inc_mistakes(1, 1, test_db)

        # Проверяем что изменилась только статистика пользователя 1
        stat1 = (
            test_db.query(Statistic)
            .filter(Statistic.user_id == 1, Statistic.card_id == 1)
            .first()
        )
        stat2 = (
            test_db.query(Statistic)
            .filter(Statistic.user_id == 2, Statistic.card_id == 1)
            .first()
        )

        assert stat1.mistakes_count == 6
        assert stat2.mistakes_count == 3  # Не изменилось
