import pytest
from unittest.mock import Mock

from tprep.infrastructure.user.user import User
from tprep.infrastructure.user.user_repo import UserRepo
from tprep.infrastructure.exam.exam import Exam
from tprep.infrastructure.exceptions.user_not_found import UserNotFound


class TestUserRepoCheckUserExists:
    def test_check_user_exists_returns_true_when_user_exists(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = UserRepo.check_user_exists(mock_user.id, mock_db)

        assert result is True
        mock_db.query.assert_called_once_with(User)

    def test_check_user_exists_returns_false_when_user_does_not_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = UserRepo.check_user_exists(999, mock_db)

        assert result is False

    def test_check_user_exists_with_negative_id(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = UserRepo.check_user_exists(-1, mock_db)

        assert result is False


class TestUserRepoCheckThatUserIsCreator:
    def test_check_that_user_is_creator_returns_true_when_user_is_creator(
        self, mock_db
    ):
        mock_exam = Mock(spec=Exam)
        mock_exam.id = 1
        mock_exam.creator_id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_exam

        result = UserRepo.check_that_user_is_creator(1, 1, mock_db)

        assert result is True
        mock_db.query.assert_called_once_with(Exam)

    def test_check_that_user_is_creator_returns_false_when_user_is_not_creator(
        self, mock_db
    ):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = UserRepo.check_that_user_is_creator(2, 1, mock_db)

        assert result is False

    def test_check_that_user_is_creator_returns_false_when_exam_does_not_exist(
        self, mock_db
    ):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = UserRepo.check_that_user_is_creator(1, 999, mock_db)

        assert result is False


class TestUserRepoGetUserByEmail:
    def test_get_user_by_email_returns_user_when_exists(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = UserRepo.get_user_by_email(mock_user.email, mock_db)

        assert result == mock_user
        assert result.id == mock_user.id
        assert result.email == mock_user.email

    def test_get_user_by_email_raises_exception_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(UserNotFound):
            UserRepo.get_user_by_email("nonexistent@example.com", mock_db)

    def test_get_user_by_email_with_empty_string(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(UserNotFound):
            UserRepo.get_user_by_email("", mock_db)


class TestUserRepoRegisterUser:
    def test_register_user_adds_user_to_database(self, mock_db, mock_user):
        result = UserRepo.register_user(mock_user, mock_db)

        mock_db.add.assert_called_once_with(mock_user)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user)
        assert result == mock_user

    def test_register_user_returns_user_with_id(self, mock_db):
        new_user = Mock(spec=User)
        new_user.id = 42
        new_user.email = "new@example.com"

        result = UserRepo.register_user(new_user, mock_db)

        assert result.id == 42
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_register_user_persists_all_fields(self, mock_db):
        new_user = Mock(spec=User)
        new_user.id = 1
        new_user.email = "fulluser@example.com"
        new_user.user_name = "Full User"
        new_user.password_hash = "hashed_password"

        result = UserRepo.register_user(new_user, mock_db)

        assert result.email == "fulluser@example.com"
        assert result.user_name == "Full User"
        assert result.password_hash == "hashed_password"
        mock_db.commit.assert_called_once()
