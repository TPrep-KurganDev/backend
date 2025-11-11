import pytest
from unittest.mock import patch

from tprep.domain.services.session_factory import SessionFactory, strategy_enum
from tprep.domain.exam_session import ExamSession
from tprep.infrastructure.user.user import User
from tprep.infrastructure.exam.exam import Exam
from tprep.infrastructure.exceptions.exam_has_no_cards import ExamHasNoCards
from tprep.infrastructure.exceptions.UnexceptableStrategy import UnexceptableStrategy


class TestSessionFactoryCreateSessionFull:
    def test_create_session_full_strategy(self, test_db, populate_db):
        # Заполняем БД
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()

        session = SessionFactory.create_session(user, exam, strategy="full", db=test_db)

        assert isinstance(session, ExamSession)
        assert session.user_id == user.id
        assert session.exam_id == exam.id
        assert len(session.questions) == 3

    def test_create_session_full_strategy_stores_in_session_ids(
        self, test_db, populate_db
    ):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()
        SessionFactory.session_ids.clear()

        session = SessionFactory.create_session(user, exam, strategy="full", db=test_db)

        assert session.id in SessionFactory.session_ids
        assert SessionFactory.session_ids[session.id] == session

    def test_create_session_full_strategy_raises_exception_with_no_cards(
        self, test_db, populate_db
    ):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()

        with pytest.raises(ExamHasNoCards) as exc_info:
            SessionFactory.create_session(user, exam, strategy="full", db=test_db)

        assert "Exam has no cards" in str(exc_info.value)


class TestSessionFactoryCreateSessionRandom:
    def test_create_session_random_strategy_with_n(self, test_db, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()

        session = SessionFactory.create_session(
            user, exam, strategy="random", n=2, db=test_db
        )

        assert isinstance(session, ExamSession)
        assert len(session.questions) == 2

    def test_create_session_random_strategy_without_n_uses_all(
        self, test_db, populate_db
    ):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()

        session = SessionFactory.create_session(
            user, exam, strategy="random", db=test_db
        )

        assert len(session.questions) == 3  # All cards

    def test_create_session_random_strategy_n_larger_than_cards(
        self, test_db, populate_db
    ):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()

        session = SessionFactory.create_session(
            user, exam, strategy="random", n=10, db=test_db
        )

        assert len(session.questions) == 3

    def test_create_session_random_strategy_n_zero(self, test_db, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()

        session = SessionFactory.create_session(
            user, exam, strategy="random", n=0, db=test_db
        )

        assert len(session.questions) == 0


class TestSessionFactoryCreateSessionSmart:
    @patch.object(SessionFactory, "get_smart_cards")
    @patch.object(SessionFactory, "smart_session_size")
    def test_create_session_smart_strategy(
        self, mock_size, mock_get_smart, test_db, populate_db
    ):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()

        mock_size.return_value = 2
        mock_get_smart.return_value = [1, 3]  # card_ids

        session = SessionFactory.create_session(
            user, exam, strategy="smart", db=test_db
        )

        assert isinstance(session, ExamSession)
        assert len(session.questions) == 2
        mock_get_smart.assert_called_once()

    @patch.object(SessionFactory, "get_smart_cards")
    @patch.object(SessionFactory, "smart_session_size")
    def test_create_session_smart_strategy_with_no_statistics(
        self, mock_size, mock_get_smart, test_db, populate_db
    ):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()

        mock_size.return_value = 3
        mock_get_smart.return_value = []  # No statistics

        session = SessionFactory.create_session(
            user, exam, strategy="smart", db=test_db
        )

        # No statistics means no cards selected
        assert len(session.questions) == 0


class TestSessionFactoryCreateSessionInvalidStrategy:
    def test_create_session_invalid_strategy(self, test_db, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()

        with pytest.raises(UnexceptableStrategy) as exc_info:
            SessionFactory.create_session(user, exam, strategy="invalid", db=test_db)

        assert "Unknow strategy: invalid" in str(exc_info.value)

    def test_strategy_enum_contains_valid_strategies(self):
        assert "full" in strategy_enum
        assert "random" in strategy_enum
        assert "smart" in strategy_enum
        assert len(strategy_enum) == 3


class TestSessionFactoryGetSessionById:
    def test_get_session_by_id_returns_existing_session(self, test_db, populate_db):
        from uuid import uuid4

        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()
        SessionFactory.session_ids.clear()

        session = SessionFactory.create_session(user, exam, db=test_db)

        session_id = str(uuid4())
        session.id = session_id

        SessionFactory.session_ids.clear()
        SessionFactory.session_ids[session_id] = session

        retrieved = SessionFactory.get_session_by_id(session_id)

        assert retrieved is not None
        assert retrieved.id == session_id
        assert retrieved.user_id == user.id

    def test_get_session_by_id_raises_key_error_for_nonexistent(self):
        SessionFactory.session_ids.clear()

        with pytest.raises(KeyError):
            SessionFactory.get_session_by_id("nonexistent-id")


class TestSessionFactoryGetSmartCards:
    def test_get_smart_cards_returns_cards_ordered_by_mistakes(
        self, test_db, populate_db
    ):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
            statistics=[
                {
                    "id": 1,
                    "user_id": 1,
                    "card_id": 3,
                    "exam_id": 1,
                    "mistakes_count": 8,
                },
                {
                    "id": 2,
                    "user_id": 1,
                    "card_id": 1,
                    "exam_id": 1,
                    "mistakes_count": 5,
                },
                {
                    "id": 3,
                    "user_id": 1,
                    "card_id": 2,
                    "exam_id": 1,
                    "mistakes_count": 2,
                },
            ],
        )

        cards = SessionFactory.get_smart_cards(1, 1, limit=3, db=test_db)

        assert len(cards) == 3
        assert cards == [3, 1, 2]  # Отсортированы по убыванию mistakes_count

    def test_get_smart_cards_respects_limit(self, test_db, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
            statistics=[
                {
                    "id": 1,
                    "user_id": 1,
                    "card_id": 3,
                    "exam_id": 1,
                    "mistakes_count": 8,
                },
                {
                    "id": 2,
                    "user_id": 1,
                    "card_id": 1,
                    "exam_id": 1,
                    "mistakes_count": 5,
                },
            ],
        )

        cards = SessionFactory.get_smart_cards(1, 1, limit=2, db=test_db)

        assert len(cards) == 2

    def test_get_smart_cards_returns_empty_when_no_statistics(
        self, test_db, populate_db
    ):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
        )

        cards = SessionFactory.get_smart_cards(1, 1, limit=10, db=test_db)

        assert cards == []


class TestSessionFactorySmartSessionSize:
    def test_smart_session_size_with_zero_cards(self):
        result = SessionFactory.smart_session_size(0)
        assert result == 0

    def test_smart_session_size_with_one_card(self):
        result = SessionFactory.smart_session_size(1)
        assert result == 1

    def test_smart_session_size_with_small_number(self):
        result = SessionFactory.smart_session_size(5)
        assert result >= 1
        assert isinstance(result, int)

    def test_smart_session_size_always_returns_at_least_one(self):
        for cards_count in [1, 2, 3, 5, 10, 50, 100]:
            result = SessionFactory.smart_session_size(cards_count)
            assert result >= 1

    def test_smart_session_size_formula(self):
        cards_count = 10
        result = SessionFactory.smart_session_size(cards_count)

        expected = 10
        assert result == expected


class TestSessionFactoryMultipleSessions:
    def test_create_multiple_sessions_for_same_user(self, test_db, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()
        SessionFactory.session_ids.clear()

        session1 = SessionFactory.create_session(user, exam, db=test_db)
        session2 = SessionFactory.create_session(user, exam, db=test_db)

        assert session1.id != session2.id
        assert len(SessionFactory.session_ids) == 2

    def test_create_sessions_for_different_users(self, test_db, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                },
                {
                    "id": 2,
                    "email": "user2@example.com",
                    "user_name": "User Two",
                    "password_hash": "hash2",
                },
            ],
            exams=[{"id": 1, "title": "Mock Exam", "creator_id": 1}],
            cards=[
                {
                    "card_id": 1,
                    "exam_id": 1,
                    "question": "Q1?",
                    "answer": "A1",
                    "number": 1,
                },
                {
                    "card_id": 2,
                    "exam_id": 1,
                    "question": "Q2?",
                    "answer": "A2",
                    "number": 2,
                },
                {
                    "card_id": 3,
                    "exam_id": 1,
                    "question": "Q3?",
                    "answer": "A3",
                    "number": 3,
                },
            ],
        )

        user = test_db.query(User).filter(User.id == 1).first()
        user_2 = test_db.query(User).filter(User.id == 2).first()
        exam = test_db.query(Exam).filter(Exam.id == 1).first()
        SessionFactory.session_ids.clear()

        session1 = SessionFactory.create_session(user, exam, db=test_db)
        session2 = SessionFactory.create_session(user_2, exam, db=test_db)

        assert session1.user_id == user.id
        assert session2.user_id == user_2.id
        assert len(SessionFactory.session_ids) == 2
