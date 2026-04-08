import pytest
import uuid

from tprep.infrastructure import Exam, Card
from tprep.infrastructure.exam.exam_repo import ExamRepo
from tprep.infrastructure.exceptions.exam_not_found import ExamNotFound
from tprep.infrastructure.exceptions.user_not_found import UserNotFound
from tprep.app.exam_schemas import ExamCreate
from tprep.infrastructure.exceptions.card_not_found import CardNotFound
from tprep.app.card_schemas import CardBase


class TestExamRepoGetExam:
    @pytest.mark.parametrize(
        "title",
        [
            "Mock Exam",
            "Mock Exam 2",
            "Empty Exam",
        ],
    )
    def test_get_exam_returns_exam_when_exists(
            self, test_db, populate_db, title
    ):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())

        if title == "Empty Exam":
            creator_id = str(uuid.uuid4())
            users_data = [
                {
                    "id": user_id,
                    "email": "user1@example.com",
                    "user_name": "User1",
                    "password_hash": "hash",
                },
                {
                    "id": creator_id,
                    "email": "user2@example.com",
                    "user_name": "User2",
                    "password_hash": "hash",
                }
            ]
        else:
            creator_id = user_id
            users_data = [
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ]

        populate_db(
            users=users_data,
            exams=[{"id": exam_id, "title": title, "creator_id": creator_id}],
        )

        result = ExamRepo.get_exam(exam_id, test_db)

        assert str(result.id) == exam_id
        assert result.title == title
        assert str(result.creator_id) == creator_id

    def test_get_exam_raises_exception_when_not_found(self, test_db):
        fake_id = str(uuid.uuid4())
        with pytest.raises(ExamNotFound):
            ExamRepo.get_exam(fake_id, test_db)


class TestExamRepoUpdateExam:
    @pytest.mark.parametrize(
        "title",
        [
            "Mock Exam",
            "Mock Exam 2",
        ],
    )
    def test_update_exam_updates_title(
            self, test_db, populate_db, title
    ):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": title, "creator_id": user_id}],
        )

        new_exam_data = ExamCreate(title="Updated Title")
        result = ExamRepo.update_exam(exam_id, new_exam_data, test_db)

        assert result.title == "Updated Title"
        assert str(result.id) == exam_id

    def test_update_exam_raises_exception_when_exam_not_found(self, test_db):
        exam_data = ExamCreate(title="New Title")
        fake_id = str(uuid.uuid4())

        with pytest.raises(ExamNotFound):
            ExamRepo.update_exam(fake_id, exam_data, test_db)


class TestExamRepoAddExam:
    @pytest.mark.parametrize(
        "title",
        [
            "Mock Exam",
            "Mock Exam 2",
        ],
    )
    def test_add_exam_adds_exam_to_database(
            self, test_db, populate_db, title
    ):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())
        exam_id_uuid = uuid.UUID(exam_id)

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ]
        )

        new_exam = Exam(id=exam_id, title=title, creator_id=user_id)
        ExamRepo.add_exam(new_exam, user_id, test_db)

        saved_exam = test_db.query(Exam).filter(Exam.id == exam_id_uuid).first()
        assert saved_exam is not None
        assert saved_exam.title == title
        assert str(saved_exam.creator_id) == user_id

    def test_add_exam_raises_exception_when_creator_not_found(self, test_db):
        fake_user_id = str(uuid.uuid4())
        fake_exam_id = str(uuid.uuid4())

        new_exam = Exam(id=fake_exam_id, title="Test", creator_id=fake_user_id)

        with pytest.raises(UserNotFound):
            ExamRepo.add_exam(new_exam, fake_user_id, test_db)


class TestExamRepoGetExamsCreatedByUser:
    def test_get_exams_created_by_user_returns_user_exams(self, test_db, populate_db):
        user_id = str(uuid.uuid4())
        exam_id_1 = str(uuid.uuid4())
        exam_id_2 = str(uuid.uuid4())

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[
                {"id": exam_id_1, "title": "Exam 1", "creator_id": user_id},
                {"id": exam_id_2, "title": "Exam 2", "creator_id": user_id},
            ],
        )

        result = ExamRepo.get_exams_created_by_user(user_id, test_db)

        assert len(result) == 2
        titles = {e.title for e in result}
        assert titles == {"Exam 1", "Exam 2"}

    def test_get_exams_created_by_user_returns_empty_list_when_no_exams(
            self, test_db, populate_db
    ):
        user_id = str(uuid.uuid4())

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ]
        )

        result = ExamRepo.get_exams_created_by_user(user_id, test_db)

        assert result == []

    def test_get_exams_created_by_user_raises_exception_when_user_not_found(
            self, test_db
    ):
        fake_id = str(uuid.uuid4())
        with pytest.raises(UserNotFound):
            ExamRepo.get_exams_created_by_user(fake_id, test_db)


class TestExamRepoGetExamsPinnedByUser:
    @pytest.mark.parametrize(
        "title",
        [
            "Mock Exam",
            "Mock Exam 2",
        ],
    )
    def test_get_exams_pinned_by_user_returns_pinned_exams(
            self, test_db, populate_db, title
    ):
        from tprep.infrastructure.exam.exam import UserExams

        user_id_1 = str(uuid.uuid4())
        user_id_2 = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())

        user_id_2_uuid = uuid.UUID(user_id_2)
        exam_id_uuid = uuid.UUID(exam_id)

        populate_db(
            users=[
                {
                    "id": user_id_1,
                    "email": f"user1{user_id_1[:6]}@example.com",
                    "user_name": "User1",
                    "password_hash": "hash",
                },
                {
                    "id": user_id_2,
                    "email": f"user2{user_id_2[:6]}@example.com",
                    "user_name": "User2",
                    "password_hash": "hash",
                },
            ],
            exams=[{"id": exam_id, "title": title, "creator_id": user_id_1}],
        )

        # ИСПРАВЛЕНИЕ: Явно указываем rights и is_pinned
        pinned = UserExams(user_id=user_id_2_uuid, exam_id=exam_id_uuid, rights="", is_pinned=True)
        test_db.add(pinned)
        test_db.commit()

        result = ExamRepo.get_exams_pinned_by_user(user_id_2, test_db)

        assert len(result) == 1
        assert str(result[0].id) == exam_id
        assert result[0].title == title

    def test_get_exams_pinned_by_user_returns_empty_list_when_no_pins(
            self, test_db, populate_db
    ):
        user_id = str(uuid.uuid4())

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ]
        )

        result = ExamRepo.get_exams_pinned_by_user(user_id, test_db)

        assert result == []

    def test_get_exams_pinned_by_user_raises_exception_when_user_not_found(
            self, test_db
    ):
        fake_id = str(uuid.uuid4())
        with pytest.raises(UserNotFound):
            ExamRepo.get_exams_pinned_by_user(fake_id, test_db)


class TestExamRepoDeleteExam:
    @pytest.mark.parametrize(
        "title",
        [
            "Mock Exam",
            "Mock Exam 2",
        ],
    )
    def test_delete_exam_removes_exam_from_database(
            self, test_db, populate_db, title
    ):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())
        exam_id_uuid = uuid.UUID(exam_id)

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": title, "creator_id": user_id}],
        )

        ExamRepo.delete_exam(exam_id, test_db)

        deleted_exam = test_db.query(Exam).filter(Exam.id == exam_id_uuid).first()
        assert deleted_exam is None

    def test_delete_exam_raises_exception_when_exam_not_found(self, test_db):
        fake_id = str(uuid.uuid4())
        with pytest.raises(ExamNotFound):
            ExamRepo.delete_exam(fake_id, test_db)


class TestExamRepoGetCardsByExamId:
    def test_returns_cards_for_exam(self, test_db, populate_db):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())
        # card_id больше не нужен, он автогенерируемый (integer)

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": "Exam", "creator_id": user_id}],
            cards=[
                # Убрали card_id из словарей
                {
                    "exam_id": exam_id,
                    "number": 1,
                    "question": "Q1",
                    "answer": "A1",
                },
                {
                    "exam_id": exam_id,
                    "number": 2,
                    "question": "Q2",
                    "answer": "A2",
                },
            ],
        )

        result = ExamRepo.get_cards_by_exam_id(exam_id, test_db)

        assert len(result) == 2
        questions = {c.question for c in result}
        assert questions == {"Q1", "Q2"}

    def test_returns_empty_list_when_no_cards(self, test_db, populate_db):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": "Exam", "creator_id": user_id}],
        )

        result = ExamRepo.get_cards_by_exam_id(exam_id, test_db)
        assert result == []


class TestExamRepoGetCard:
    def test_get_card_success(self, test_db, populate_db):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())
        # card_id не передаем, он будет сгенерирован БД (1, 2, ...)
        # Но нам нужно знать, какой ID получила карта, чтобы её найти.
        # Проще найти карту по вопросу или взять первую после создания.

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": "Exam", "creator_id": user_id}],
            cards=[
                {
                    "exam_id": exam_id,
                    "number": 1,
                    "question": "UniqueQuestionForTest",
                    "answer": "A",
                }
            ],
        )

        # Находим карту по вопросу, так как ID мы не знаем заранее
        # Или можно получить все карты экзамена и взять нужную
        all_cards = ExamRepo.get_cards_by_exam_id(exam_id, test_db)
        target_card = next(c for c in all_cards if c.question == "UniqueQuestionForTest")

        # Теперь тестируем get_card с реальным ID
        card = ExamRepo.get_card(target_card.card_id, test_db)

        assert card.question == "UniqueQuestionForTest"
        # card_id теперь integer, сравниваем напрямую
        assert card.card_id == target_card.card_id

    def test_get_card_raises_when_not_found(self, test_db):
        # Передаем несуществующий integer ID
        with pytest.raises(CardNotFound):
            ExamRepo.get_card(999999, test_db)


class TestExamRepoCreateCard:
    def test_create_card_assigns_correct_number(self, test_db, populate_db):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": "Exam", "creator_id": user_id}],
            cards=[
                # Убрали card_id
                {
                    "exam_id": exam_id,
                    "number": 1,
                    "question": "Q1",
                    "answer": "A1",
                },
                {
                    "exam_id": exam_id,
                    "number": 2,
                    "question": "Q2",
                    "answer": "A2",
                },
            ],
        )

        card = ExamRepo.create_card(exam_id, test_db)

        assert card.number == 3
        assert str(card.exam_id) == exam_id


class TestExamRepoUpdateCard:
    def test_update_card_updates_fields(self, test_db, populate_db):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": "Exam", "creator_id": user_id}],
            cards=[
                {
                    "exam_id": exam_id,
                    "number": 1,
                    "question": "Old",
                    "answer": "Old",
                }
            ],
        )

        # Получаем созданный ID карты
        created_card = test_db.query(Card).filter(Card.exam_id == uuid.UUID(exam_id)).first()
        card_id = created_card.card_id

        card_data = CardBase(question="New", answer="New")
        card = ExamRepo.update_card(exam_id, card_id, card_data, test_db)

        assert card.question == "New"
        assert card.answer == "New"

    def test_update_card_raises_when_not_found(self, test_db):
        fake_exam_id = str(uuid.uuid4())
        # Несуществующий integer ID
        with pytest.raises(CardNotFound):
            ExamRepo.update_card(fake_exam_id, 999999, CardBase(question="Q", answer="A"), test_db)


class TestExamRepoDeleteCard:
    def test_delete_card_removes_card(self, test_db, populate_db):
        user_id = str(uuid.uuid4())
        exam_id = str(uuid.uuid4())

        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": f"user{user_id[:8]}@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": exam_id, "title": "Exam", "creator_id": user_id}],
            cards=[
                {
                    "exam_id": exam_id,
                    "number": 1,
                    "question": "Q",
                    "answer": "A",
                }
            ],
        )

        # Получаем ID созданной карты
        created_card = test_db.query(Card).filter(Card.exam_id == uuid.UUID(exam_id)).first()
        card_id = created_card.card_id

        ExamRepo.delete_card(exam_id, card_id, test_db)

        card = test_db.query(Card).filter(Card.card_id == card_id).first()
        assert card is None