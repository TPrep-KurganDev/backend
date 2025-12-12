from http import HTTPStatus

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tprep.app.api.routes.auth import router
from tprep.infrastructure.database import get_db
from tprep.infrastructure.authorization import hash_password, create_access_token
from tprep.app.authorization_schemas import TokenData
from tprep.infrastructure.exceptions.invalid_or_expired_token import InvalidOrExpiredToken
from tprep.infrastructure.exceptions.user_already_exists import UserAlreadyExists
from tprep.infrastructure.exceptions.wrong_login_or_password import WrongLoginOrPassword
from tprep.infrastructure.user.user import User
from config import settings



@pytest.fixture
def app(test_db):
    app = FastAPI()
    app.include_router(router)

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestAuthRegister:
    def test_register_user_success(self, client):
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "user_name": "test",
                "password": "secret",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["user_name"] == "test"

    def test_register_user_already_exists(self, client, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "test",
                    "password_hash": hash_password("secret"),
                }
            ]
        )

        with pytest.raises(UserAlreadyExists):
            client.post(
                "/auth/register",
                json={
                    "email": "test@example.com",
                    "user_name": "test",
                    "password": "secret",
                },
            )


class TestAuthLogin:
    def test_login_success(self, client, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "login@example.com",
                    "user_name": "loginuser",
                    "password_hash": hash_password("secret"),
                }
            ]
        )

        response = client.post(
            "/auth/login",
            json={
                "email": "login@example.com",
                "password": "secret",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 1
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)

    def test_login_wrong_password_raises(self, client, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "login@example.com",
                    "user_name": "loginuser",
                    "password_hash": hash_password("secret"),
                }
            ]
        )

        with pytest.raises(WrongLoginOrPassword):
            client.post(
                "/auth/login",
                json={
                    "email": "login@example.com",
                    "password": "wrong",
                },
            )

    def test_login_user_not_found_raises(self, client):
        with pytest.raises(WrongLoginOrPassword):
            client.post(
                "/auth/login",
                json={
                    "email": "missing@example.com",
                    "password": "secret",
                },
            )


class TestAuthTokenSwagger:
    def test_login_for_swagger_success(self, client, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "swagger@example.com",
                    "user_name": "swagger",
                    "password_hash": hash_password("secret"),
                }
            ]
        )

        response = client.post(
            "/auth/token",
            data={
                "username": "swagger@example.com",
                "password": "secret",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 1
        assert data["token_type"] == "bearer"

    def test_login_for_swagger_wrong_password_raises(self, client, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "swagger@example.com",
                    "user_name": "swagger",
                    "password_hash": hash_password("secret"),
                }
            ]
        )

        with pytest.raises(WrongLoginOrPassword):
            client.post(
                "/auth/token",
                data={
                    "username": "swagger@example.com",
                    "password": "wrong",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

    def test_login_for_swagger_user_not_found_raises(self, client):
        with pytest.raises(WrongLoginOrPassword):
            client.post(
                "/auth/token",
                data={
                    "username": "missing@example.com",
                    "password": "secret",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
