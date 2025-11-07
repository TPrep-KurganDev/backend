import pytest
from unittest.mock import Mock, patch

from tprep.infrastructure.exam.exam import Exam, UserPinnedExam, Card
from tprep.infrastructure.exam.exam_repo import ExamRepo
from tprep.infrastructure.exceptions.exam_not_found import ExamNotFound
from tprep.infrastructure.exceptions.user_not_found import UserNotFound
from tprep.app.exam_schemas import ExamCreate


class TestExamRepoGetExam:
    def test_get_exam_returns_exam_when_exists(self, mock_db, mock_exam):
        mock_db.query.return_value.filter.return_value.first.return_value = mock_exam

        result = ExamRepo.get_exam(mock_exam.id, mock_db)

        assert result == mock_exam
        mock_db.query.assert_called_once_with(Exam)

    def test_get_exam_raises_exception_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ExamNotFound):
            ExamRepo.get_exam(999, mock_db)


class TestExamRepoUpdateExam:
    @patch.object(ExamRepo, 'get_exam')
    def test_update_exam_updates_title(self, mock_get_exam, mock_db, mock_exam):
        mock_get_exam.return_value = mock_exam
        exam_data = ExamCreate(title="Updated Title")

        result = ExamRepo.update_exam(mock_exam.id, exam_data, mock_db)

        assert result.title == "Updated Title"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @patch.object(ExamRepo, 'get_exam')
    def test_update_exam_raises_exception_when_exam_not_found(self, mock_get_exam, mock_db):
        mock_get_exam.side_effect = ExamNotFound

        exam_data = ExamCreate(title="New Title")

        with pytest.raises(ExamNotFound):
            ExamRepo.update_exam(999, exam_data, mock_db)


class TestExamRepoAddExam:
    @patch('tprep.infrastructure.exam.exam_repo.UserRepo.check_user_exists')
    def test_add_exam_adds_exam_to_database(self, mock_check, mock_db, mock_exam):
        mock_check.return_value = True

        ExamRepo.add_exam(mock_exam, mock_exam.creator_id, mock_db)

        mock_db.add.assert_called_once_with(mock_exam)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @patch('tprep.infrastructure.exam.exam_repo.UserRepo.check_user_exists')
    def test_add_exam_raises_exception_when_creator_not_found(self, mock_check, mock_db):
        mock_check.return_value = False
        new_exam = Mock(spec=Exam)

        with pytest.raises(UserNotFound):
            ExamRepo.add_exam(new_exam, 999, mock_db)


class TestExamRepoGetExamsCreatedByUser:

    @patch('tprep.infrastructure.exam.exam_repo.UserRepo.check_user_exists')
    def test_get_exams_created_by_user_returns_user_exams(
        self, mock_check, mock_db, mock_exam, mock_exam_2
    ):
        mock_check.return_value = True
        mock_db.query.return_value.filter.return_value.all.return_value = [
            mock_exam,
            mock_exam_2,
        ]

        result = ExamRepo.get_exams_created_by_user(1, mock_db)

        assert len(result) == 2
        assert result == [mock_exam, mock_exam_2]

    @patch('tprep.infrastructure.exam.exam_repo.UserRepo.check_user_exists')
    def test_get_exams_created_by_user_returns_empty_list_when_no_exams(
        self, mock_check, mock_db
    ):
        mock_check.return_value = True
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = ExamRepo.get_exams_created_by_user(1, mock_db)

        assert result == []

    @patch('tprep.infrastructure.exam.exam_repo.UserRepo.check_user_exists')
    def test_get_exams_created_by_user_raises_exception_when_user_not_found(
        self, mock_check, mock_db
    ):
        mock_check.return_value = False

        with pytest.raises(UserNotFound):
            ExamRepo.get_exams_created_by_user(999, mock_db)


class TestExamRepoGetExamsPinnedByUser:
    @patch('tprep.infrastructure.exam.exam_repo.UserRepo.check_user_exists')
    def test_get_exams_pinned_by_user_returns_pinned_exams(
        self, mock_check, mock_db, mock_exam
    ):
        mock_check.return_value = True
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [
            mock_exam
        ]

        result = ExamRepo.get_exams_pinned_by_user(2, mock_db)

        assert len(result) == 1
        assert result[0] == mock_exam

    @patch('tprep.infrastructure.exam.exam_repo.UserRepo.check_user_exists')
    def test_get_exams_pinned_by_user_returns_empty_list_when_no_pins(
        self, mock_check, mock_db
    ):
        mock_check.return_value = True
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = []

        result = ExamRepo.get_exams_pinned_by_user(1, mock_db)

        assert result == []

    @patch('tprep.infrastructure.exam.exam_repo.UserRepo.check_user_exists')
    def test_get_exams_pinned_by_user_raises_exception_when_user_not_found(
        self, mock_check, mock_db
    ):
        mock_check.return_value = False

        with pytest.raises(UserNotFound):
            ExamRepo.get_exams_pinned_by_user(999, mock_db)


class TestExamRepoDeleteExam:
    @patch.object(ExamRepo, 'get_exam')
    def test_delete_exam_removes_exam_from_database(self, mock_get_exam, mock_db, mock_exam):
        mock_get_exam.return_value = mock_exam

        ExamRepo.delete_exam(mock_exam.id, mock_db)

        mock_db.delete.assert_called_once_with(mock_exam)
        mock_db.commit.assert_called_once()

    @patch.object(ExamRepo, 'get_exam')
    def test_delete_exam_raises_exception_when_exam_not_found(self, mock_get_exam, mock_db):
        mock_get_exam.side_effect = ExamNotFound

        with pytest.raises(ExamNotFound):
            ExamRepo.delete_exam(999, mock_db)