import pytest

from tprep.infrastructure import Exam, Card
from tprep.infrastructure.exam.exam_repo import ExamRepo
from tprep.infrastructure.exceptions.exam_not_found import ExamNotFound
from tprep.infrastructure.exceptions.user_not_found import UserNotFound
from tprep.app.exam_schemas import ExamCreate
from tprep.infrastructure.exceptions.card_not_found import CardNotFound
from tprep.app.card_schemas import CardBase


class TestExamRepoGetExam:
    @pytest.mark.parametrize(
        "exam_id,title,creator_id",
        [
            (1, "Mock Exam", 1),
            (2, "Mock Exam 2", 1),
            (3, "Empty Exam", 2),
        ],
    )
    def test_get_exam_returns_exam_when_exists(
        self, test_db, populate_db, exam_id, title, creator_id
    ):
        # Создаем пользователя и экзамен в БД
        populate_db(
            users=[
                {
                    "id": creator_id,
                    "email": f"user{creator_id}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": title, "creator_id": creator_id}],
        )

        result = ExamRepo.get_exam(exam_id, test_db)

        assert result.id == exam_id
        assert result.title == title
        assert result.creator_id == creator_id

    def test_get_exam_raises_exception_when_not_found(self, test_db):
        with pytest.raises(ExamNotFound):
            ExamRepo.get_exam(999, test_db)


class TestExamRepoUpdateExam:
    @pytest.mark.parametrize(
        "exam_id,title,creator_id",
        [
            (1, "Mock Exam", 1),
            (2, "Mock Exam 2", 1),
        ],
    )
    def test_update_exam_updates_title(
        self, test_db, populate_db, exam_id, title, creator_id
    ):
        populate_db(
            users=[
                {
                    "id": creator_id,
                    "email": f"user{creator_id}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": title, "creator_id": creator_id}],
        )

        new_exam_data = ExamCreate(title="Updated Title")
        result = ExamRepo.update_exam(exam_id, new_exam_data, test_db)

        assert result.title == "Updated Title"
        assert result.id == exam_id

    def test_update_exam_raises_exception_when_exam_not_found(self, test_db):
        exam_data = ExamCreate(title="New Title")

        with pytest.raises(ExamNotFound):
            ExamRepo.update_exam(999, exam_data, test_db)


class TestExamRepoAddExam:
    @pytest.mark.parametrize(
        "exam_id,title,creator_id",
        [
            (1, "Mock Exam", 1),
            (2, "Mock Exam 2", 1),
        ],
    )
    def test_add_exam_adds_exam_to_database(
        self, test_db, populate_db, exam_id, title, creator_id
    ):
        # Создаем пользователя
        populate_db(
            users=[
                {
                    "id": creator_id,
                    "email": f"user{creator_id}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ]
        )

        new_exam = Exam(id=exam_id, title=title, creator_id=creator_id)
        ExamRepo.add_exam(new_exam, creator_id, test_db)

        # Проверяем что экзамен в БД
        saved_exam = test_db.query(Exam).filter(Exam.id == exam_id).first()
        assert saved_exam is not None
        assert saved_exam.title == title
        assert saved_exam.creator_id == creator_id

    def test_add_exam_raises_exception_when_creator_not_found(self, test_db):
        new_exam = Exam(id=1, title="Test", creator_id=999)

        with pytest.raises(UserNotFound):
            ExamRepo.add_exam(new_exam, 999, test_db)


class TestExamRepoGetExamsCreatedByUser:
    def test_get_exams_created_by_user_returns_user_exams(self, test_db, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "user1@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[
                {"id": 1, "title": "Exam 1", "creator_id": 1},
                {"id": 2, "title": "Exam 2", "creator_id": 1},
            ],
        )

        result = ExamRepo.get_exams_created_by_user(1, test_db)

        assert len(result) == 2
        assert result[0].title == "Exam 1"
        assert result[1].title == "Exam 2"

    def test_get_exams_created_by_user_returns_empty_list_when_no_exams(
        self, test_db, populate_db
    ):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "user1@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ]
        )

        result = ExamRepo.get_exams_created_by_user(1, test_db)

        assert result == []

    def test_get_exams_created_by_user_raises_exception_when_user_not_found(
        self, test_db
    ):
        with pytest.raises(UserNotFound):
            ExamRepo.get_exams_created_by_user(999, test_db)


class TestExamRepoGetExamsPinnedByUser:
    @pytest.mark.parametrize(
        "exam_id,title",
        [
            (1, "Mock Exam"),
            (2, "Mock Exam 2"),
        ],
    )
    def test_get_exams_pinned_by_user_returns_pinned_exams(
        self, test_db, populate_db, exam_id, title
    ):
        from tprep.infrastructure.exam.exam import UserPinnedExam

        # Создаем пользователей и экзамены
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
            exams=[{"id": exam_id, "title": title, "creator_id": 1}],
        )

        # Создаем связь (пользователь 2 закрепил экзамен)
        pinned = UserPinnedExam(user_id=2, exam_id=exam_id)
        test_db.add(pinned)
        test_db.commit()

        result = ExamRepo.get_exams_pinned_by_user(2, test_db)

        assert len(result) == 1
        assert result[0].id == exam_id
        assert result[0].title == title

    def test_get_exams_pinned_by_user_returns_empty_list_when_no_pins(
        self, test_db, populate_db
    ):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "user1@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ]
        )

        result = ExamRepo.get_exams_pinned_by_user(1, test_db)

        assert result == []

    def test_get_exams_pinned_by_user_raises_exception_when_user_not_found(
        self, test_db
    ):
        with pytest.raises(UserNotFound):
            ExamRepo.get_exams_pinned_by_user(999, test_db)


class TestExamRepoDeleteExam:
    @pytest.mark.parametrize(
        "exam_id,title",
        [
            (1, "Mock Exam"),
            (2, "Mock Exam 2"),
        ],
    )
    def test_delete_exam_removes_exam_from_database(
        self, test_db, populate_db, exam_id, title
    ):
        # Создаем пользователя и экзамен
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "user1@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": title, "creator_id": 1}],
        )

        ExamRepo.delete_exam(exam_id, test_db)

        # Проверяем что экзамен удален
        deleted_exam = test_db.query(Exam).filter(Exam.id == exam_id).first()
        assert deleted_exam is None

    def test_delete_exam_raises_exception_when_exam_not_found(self, test_db):
        with pytest.raises(ExamNotFound):
            ExamRepo.delete_exam(999, test_db)


class TestExamRepoGetCardsByExamId:
    def test_returns_cards_for_exam(self, test_db, populate_db):
        populate_db(
            users=[{
                "id": 1,
                "email": "user@example.com",
                "user_name": "User",
                "password_hash": "hash",
            }],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
            cards=[
                {"card_id": 1, "exam_id": 1, "number": 1, "question": "Q1", "answer": "A1"},
                {"card_id": 2, "exam_id": 1, "number": 2, "question": "Q2", "answer": "A2"},
            ],
        )

        result = ExamRepo.get_cards_by_exam_id(1, test_db)

        assert len(result) == 2
        assert result[0].question == "Q1"
        assert result[1].question == "Q2"

    def test_returns_empty_list_when_no_cards(self, test_db, populate_db):
        populate_db(
            users=[{
                "id": 1,
                "email": "user@example.com",
                "user_name": "User",
                "password_hash": "hash",
            }],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
        )

        result = ExamRepo.get_cards_by_exam_id(1, test_db)
        assert result == []


class TestExamRepoGetCard:
    def test_get_card_success(self, test_db, populate_db):
        populate_db(
            users=[{
                "id": 1,
                "email": "user@example.com",
                "user_name": "User",
                "password_hash": "hash",
            }],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
            cards=[{
                "card_id": 10,
                "exam_id": 1,
                "number": 1,
                "question": "Q",
                "answer": "A",
            }],
        )

        card = ExamRepo.get_card(10, test_db)

        assert card.card_id == 10
        assert card.question == "Q"

    def test_get_card_raises_when_not_found(self, test_db):
        with pytest.raises(CardNotFound):
            ExamRepo.get_card(999, test_db)


class TestExamRepoCreateCard:
    def test_create_card_assigns_correct_number(self, test_db, populate_db):
        populate_db(
            users=[{
                "id": 1,
                "email": "user@example.com",
                "user_name": "User",
                "password_hash": "hash",
            }],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
            cards=[
                {"card_id": 12, "exam_id": 1, "number": 1, "question": "Q1", "answer": "A1"},
                {"card_id": 13, "exam_id": 1, "number": 2, "question": "Q2", "answer": "A2"},
            ],
        )

        card = ExamRepo.create_card(1, test_db)

        assert card.number == 3
        assert card.exam_id == 1


class TestExamRepoUpdateCard:
    def test_update_card_updates_fields(self, test_db, populate_db):
        populate_db(
            users=[{
                "id": 1,
                "email": "user@example.com",
                "user_name": "User",
                "password_hash": "hash",
            }],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
            cards=[{
                "card_id": 1,
                "exam_id": 1,
                "number": 1,
                "question": "Old",
                "answer": "Old",
            }],
        )

        card_data = CardBase(question="New", answer="New")
        card = ExamRepo.update_card(1, 1, card_data, test_db)

        assert card.question == "New"
        assert card.answer == "New"

    def test_update_card_raises_when_not_found(self, test_db):
        with pytest.raises(CardNotFound):
            ExamRepo.update_card(1, 999, CardBase(question="Q", answer="A"), test_db)


class TestExamRepoDeleteCard:
    def test_delete_card_removes_card(self, test_db, populate_db):
        populate_db(
            users=[{
                "id": 1,
                "email": "user@example.com",
                "user_name": "User",
                "password_hash": "hash",
            }],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
            cards=[{
                "card_id": 1,
                "exam_id": 1,
                "number": 1,
                "question": "Q",
                "answer": "A",
            }],
        )

        ExamRepo.delete_card(1, 1, test_db)

        card = test_db.query(Card).filter(Card.card_id == 1).first()
        assert card is None


class TestExamRepoPinning:
    def test_pin_and_check_exam(self, test_db, populate_db):
        populate_db(
            users=[
                {"id": 1, "email": "u1@example.com", "user_name": "U1", "password_hash": "hash"},
                {"id": 2, "email": "u2@example.com", "user_name": "U2", "password_hash": "hash"},
            ],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
        )

        ExamRepo.pin_exam(2, 1, test_db)

        assert ExamRepo.check_pinned_exam(2, 1, test_db) is True

    def test_unpin_exam(self, test_db, populate_db):
        populate_db(
            users=[
                {"id": 1, "email": "u1@example.com", "user_name": "U1", "password_hash": "hash"},
                {"id": 2, "email": "u2@example.com", "user_name": "U2", "password_hash": "hash"},
            ],
            exams=[{"id": 1, "title": "Exam", "creator_id": 1}],
        )

        ExamRepo.pin_exam(2, 1, test_db)
        ExamRepo.unpin_exam(2, 1, test_db)

        assert ExamRepo.check_pinned_exam(2, 1, test_db) is False
