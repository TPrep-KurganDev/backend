import pytest
from datetime import datetime, timedelta
from jose import jwt

from tprep.app.authorization_schemas import TokenData
from tprep.infrastructure.authorization import (
    JWT_PURPOSE_ACCESS,
    JWT_PURPOSE_REFRESH,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user,
)
from tprep.infrastructure.exceptions.invalid_or_expired_token import (
    InvalidOrExpiredToken,
)
from config import settings


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        password = "my_secure_password"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_each_time(self):
        password = "my_secure_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        password = "my_secure_password"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "my_secure_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_string(self):
        password = "my_secure_password"
        hashed = hash_password(password)
        assert verify_password("", hashed) is False


class TestAccessToken:
    def test_create_access_token_returns_string(self):
        data = TokenData(sub="123")
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_data(self):
        data = TokenData(sub="123", login="test@example.com")
        token = create_access_token(data)

        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )
        assert decoded["sub"] == "123"
        assert decoded["login"] == "test@example.com"
        assert decoded["purpose"] == JWT_PURPOSE_ACCESS
        assert "exp" in decoded

    def test_create_access_token_has_expiration(self):
        data = TokenData(sub="123")
        token = create_access_token(data)

        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )
        assert "exp" in decoded

    def test_create_refresh_token_contains_purpose(self):
        data = TokenData(sub="42", login="u")
        token = create_refresh_token(data)
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )
        assert decoded["sub"] == "42"
        assert decoded["purpose"] == JWT_PURPOSE_REFRESH
        assert decoded["login"] == "u"

    def test_verify_refresh_token_valid(self):
        data = TokenData(sub="99", login="name")
        token = create_refresh_token(data)
        result = verify_refresh_token(token)
        assert result.sub == "99"
        assert result.login == "name"

    def test_verify_refresh_token_rejects_access_token(self):
        data = TokenData(sub="1", login="x")
        access = create_access_token(data)

        with pytest.raises(InvalidOrExpiredToken):
            verify_refresh_token(access)

    def test_verify_refresh_token_invalid(self):
        invalid_token = "invalid.token.here"

        with pytest.raises(InvalidOrExpiredToken):
            verify_refresh_token(invalid_token)

    def test_verify_refresh_token_no_subject(self):
        expire = datetime.utcnow() + timedelta(days=7)
        bad = jwt.encode(
            {"purpose": JWT_PURPOSE_REFRESH, "exp": expire},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        with pytest.raises(InvalidOrExpiredToken):
            verify_refresh_token(bad)


class TestGetCurrentUser:
    # def test_get_current_user_missing_bearer_prefix(self, test_db, populate_db):
    #     populate_db(
    #         users=[
    #             {
    #                 "id": 42,
    #                 "email": f"user42@example.com",
    #                 "user_name": "User",
    #                 "password_hash": "hash",
    #             }
    #         ],
    #     )
    #     data = TokenData(sub="42")
    #     token = create_access_token(data)
    #
    #     with pytest.raises(InvalidAuthorizationHeader):
    #         get_current_user(token=token, db=test_db)
    #
    # def test_get_current_user_wrong_prefix(self, test_db, populate_db):
    #     populate_db(
    #         users=[
    #             {
    #                 "id": 42,
    #                 "email": f"user42@example.com",
    #                 "user_name": "User",
    #                 "password_hash": "hash",
    #             }
    #         ],
    #     )
    #     data = TokenData(sub="42")
    #     token = create_access_token(data)
    #     print(token)
    #
    #     with pytest.raises(InvalidAuthorizationHeader):
    #         get_current_user(token=token, db=test_db)

    def test_get_current_user_invalid_token(self, test_db):
        with pytest.raises(InvalidOrExpiredToken):
            get_current_user(token="invalid.token.here", db=test_db)

    def test_get_current_user_no_subject(self, test_db):
        expire = datetime.utcnow() + timedelta(minutes=60)
        data = {"exp": str(expire)}
        token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        with pytest.raises(InvalidOrExpiredToken):
            get_current_user(token=token, db=test_db)
