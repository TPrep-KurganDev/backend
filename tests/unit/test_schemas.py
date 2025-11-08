import pytest
from pydantic import ValidationError

from tprep.app.authorization_schemas import (
    LoginRequest,
    Token,
    RefreshRequest,
    AccessTokenResponse,
)
from tprep.app.user_schemas import UserBase, UserCreate, UserOut
from tprep.app.exam_schemas import ExamBase, ExamCreate, ExamOut
from tprep.app.session_schemas import ExamSessionResponse, ExamSessionStartRequest
from tprep.infrastructure.exceptions.wrong_n_value import WrongNValue


class TestLoginRequest:
    def test_login_request_valid(self):
        data = {"email": "test@example.com", "password": "password123"}
        request = LoginRequest(**data)

        assert request.email == "test@example.com"
        assert request.password == "password123"

    def test_login_request_invalid_email(self):
        data = {"email": "invalid-email", "password": "password123"}

        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)

        assert "email" in str(exc_info.value).lower()

    def test_login_request_missing_fields(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com")

        with pytest.raises(ValidationError):
            LoginRequest(password="password123")


class TestToken:
    def test_token_valid(self):
        data = {"access_token": "abc123", "token_type": "bearer"}
        token = Token(**data)

        assert token.access_token == "abc123"
        assert token.token_type == "bearer"

    def test_token_missing_fields(self):
        with pytest.raises(ValidationError):
            Token(access_token="abc123")

        with pytest.raises(ValidationError):
            Token(token_type="bearer")


class TestRefreshRequest:
    def test_refresh_request_valid(self):
        data = {"refreshToken": "refresh_token_here"}
        request = RefreshRequest(**data)

        assert request.refreshToken == "refresh_token_here"

    def test_refresh_request_missing_field(self):
        with pytest.raises(ValidationError):
            RefreshRequest()


class TestAccessTokenResponse:
    def test_access_token_response_valid(self):
        data = {
            "accessToken": "token123",
            "expiresIn": 3600,
            "token_type": "bearer"
        }
        response = AccessTokenResponse(**data)

        assert response.accessToken == "token123"
        assert response.expiresIn == 3600
        assert response.token_type == "bearer"

    def test_access_token_response_expires_in_must_be_int(self):
        data = {
            "accessToken": "token123",
            "expiresIn": "not an int",
            "token_type": "bearer"
        }

        with pytest.raises(ValidationError) as exc_info:
            AccessTokenResponse(**data)

        assert "expiresIn" in str(exc_info.value) or "expires_in" in str(exc_info.value).lower()


class TestUserSchemas:
    def test_user_base_valid(self):
        data = {"email": "user@example.com", "user_name": "John Doe"}
        user = UserBase(**data)

        assert user.email == "user@example.com"
        assert user.user_name == "John Doe"

    def test_user_base_invalid_email(self):
        data = {"email": "not-an-email", "user_name": "John Doe"}

        with pytest.raises(ValidationError):
            UserBase(**data)

    def test_user_create_includes_password(self):
        data = {
            "email": "user@example.com",
            "user_name": "John Doe",
            "password": "securepassword"
        }
        user = UserCreate(**data)

        assert user.email == "user@example.com"
        assert user.user_name == "John Doe"
        assert user.password == "securepassword"

    def test_user_create_missing_password(self):
        data = {"email": "user@example.com", "user_name": "John Doe"}

        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_out_includes_id(self):
        data = {
            "id": 1,
            "email": "user@example.com",
            "user_name": "John Doe"
        }
        user = UserOut(**data)

        assert user.id == 1
        assert user.email == "user@example.com"
        assert user.user_name == "John Doe"

    def test_user_out_missing_id(self):
        data = {"email": "user@example.com", "user_name": "John Doe"}

        with pytest.raises(ValidationError):
            UserOut(**data)


class TestExamSchemas:
    def test_exam_base_valid(self):
        data = {"title": "Math Exam"}
        exam = ExamBase(**data)

        assert exam.title == "Math Exam"

    def test_exam_base_missing_title(self):
        with pytest.raises(ValidationError):
            ExamBase()

    def test_exam_create_valid(self):
        data = {"title": "Science Exam"}
        exam = ExamCreate(**data)

        assert exam.title == "Science Exam"

    def test_exam_out_includes_id(self):
        data = {"id": 1, "title": "History Exam"}
        exam = ExamOut(**data)

        assert exam.id == 1
        assert exam.title == "History Exam"

    def test_exam_out_missing_id(self):
        data = {"title": "History Exam"}

        with pytest.raises(ValidationError):
            ExamOut(**data)


class TestExamSessionResponse:
    def test_exam_session_response_valid(self):
        from datetime import datetime

        data = {
            "id": 1,
            "created_at": datetime.utcnow(),
            "user_id": 1,
            "exam_id": 10,
            "questions": [1, 2, 3]
        }
        response = ExamSessionResponse(**data)

        assert response.id == 1
        assert response.user_id == 1
        assert response.exam_id == 10
        assert response.questions == [1, 2, 3]

    def test_exam_session_response_with_optional_fields(self):
        from datetime import datetime

        data = {
            "id": 1,
            "created_at": datetime.utcnow(),
            "user_id": 1,
            "exam_id": 10,
            "questions": [1, 2, 3],
            "answers": [True, False, True],
            "n": 3
        }
        response = ExamSessionResponse(**data)

        assert response.answers == [True, False, True]
        assert response.n == 3

    def test_exam_session_response_optional_fields_default_none(self):
        from datetime import datetime

        data = {
            "id": 1,
            "created_at": datetime.utcnow(),
            "user_id": 1,
            "exam_id": 10,
            "questions": [1, 2, 3]
        }
        response = ExamSessionResponse(**data)

        assert response.answers is None
        assert response.n is None


class TestExamSessionStartRequest:
    def test_exam_session_start_request_valid_random(self):
        data = {
            "user_id": 1,
            "exam_id": 10,
            "strategy": "random",
            "n": 5
        }
        request = ExamSessionStartRequest(**data)

        assert request.user_id == 1
        assert request.exam_id == 10
        assert request.strategy == "random"
        assert request.n == 5

    def test_exam_session_start_request_valid_full(self):
        data = {
            "user_id": 1,
            "exam_id": 10,
            "strategy": "full"
        }
        request = ExamSessionStartRequest(**data)

        assert request.strategy == "full"
        assert request.n is None

    def test_exam_session_start_request_valid_smart(self):
        data = {
            "user_id": 1,
            "exam_id": 10,
            "strategy": "smart"
        }
        request = ExamSessionStartRequest(**data)

        assert request.strategy == "smart"
        assert request.n is None

    def test_exam_session_start_request_default_strategy(self):
        data = {
            "user_id": 1,
            "exam_id": 10
        }
        request = ExamSessionStartRequest(**data)

        assert request.strategy == "random"

    def test_exam_session_start_request_smart_with_n_raises_error(self):
        data = {
            "user_id": 1,
            "exam_id": 10,
            "strategy": "smart",
            "n": 5
        }

        with pytest.raises(WrongNValue) as exc_info:
            ExamSessionStartRequest(**data)

        assert "not allowed for strategy 'smart'" in str(exc_info.value)

    def test_exam_session_start_request_full_with_n_raises_error(self):
        data = {
            "user_id": 1,
            "exam_id": 10,
            "strategy": "full",
            "n": 5
        }

        with pytest.raises(WrongNValue) as exc_info:
            ExamSessionStartRequest(**data)

        assert "not allowed for strategy 'full'" in str(exc_info.value)

    def test_exam_session_start_request_negative_n_raises_error(self):
        data = {
            "user_id": 1,
            "exam_id": 10,
            "strategy": "random",
            "n": -5
        }

        with pytest.raises(WrongNValue) as exc_info:
            ExamSessionStartRequest(**data)

        assert "must be positive" in str(exc_info.value)

    def test_exam_session_start_request_zero_n_raises_error(self):
        data = {
            "user_id": 1,
            "exam_id": 10,
            "strategy": "random",
            "n": 0
        }

        with pytest.raises(WrongNValue) as exc_info:
            ExamSessionStartRequest(**data)

        assert "must be positive" in str(exc_info.value)

    def test_exam_session_start_request_random_without_n_valid(self):
        data = {
            "user_id": 1,
            "exam_id": 10,
            "strategy": "random"
        }
        request = ExamSessionStartRequest(**data)

        assert request.strategy == "random"
        assert request.n is None