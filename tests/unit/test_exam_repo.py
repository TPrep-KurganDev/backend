import pytest

from tprep.infrastructure.exam.exam import Exam
from tprep.infrastructure.exam.exam_repo import ExamRepo
from tprep.infrastructure.exceptions.exam_not_found import ExamNotFound
from tprep.infrastructure.exceptions.user_not_found import UserNotFound
from tprep.app.exam_schemas import ExamCreate


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
        # Создаем пользователя и экзамен
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
