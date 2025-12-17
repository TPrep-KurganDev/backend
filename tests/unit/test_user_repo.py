import pytest

from tprep.infrastructure.user.user import User
from tprep.infrastructure.user.user_repo import UserRepo
from tprep.infrastructure.exceptions.user_not_found import UserNotFound


class TestUserRepoCheckUserExists:
    @pytest.mark.parametrize(
        "user_id,email,user_name,password_hash",
        [
            (1, "test@example.com", "Test User", "hashed_password"),
            (2, "user2@example.com", "User Two", "hashed_password_2"),
            (3, "admin@example.com", "Admin User", "admin_hashed_password"),
        ],
    )
    def test_check_user_exists_returns_true_when_user_exists(
        self, test_db, populate_db, user_id, email, user_name, password_hash
    ):
        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": email,
                    "user_name": user_name,
                    "password_hash": password_hash,
                }
            ]
        )

        result = UserRepo.check_user_exists(user_id, test_db)

        assert result is True

    def test_check_user_exists_returns_false_when_user_does_not_exist(self, test_db):
        result = UserRepo.check_user_exists(999, test_db)

        assert result is False

    def test_check_user_exists_with_negative_id(self, test_db):
        result = UserRepo.check_user_exists(-1, test_db)

        assert result is False


class TestUserRepoCheckThatUserIsCreator:
    def test_check_that_user_is_creator_returns_true_when_user_is_creator(
        self, test_db, populate_db
    ):
        # Создаем пользователя и экзамен
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ],
            exams=[{"id": 1, "title": "Test Exam", "creator_id": 1}],
        )

        result = UserRepo.check_that_user_is_creator(1, 1, test_db)

        assert result is True

    def test_check_that_user_is_creator_returns_false_when_user_is_not_creator(
        self, test_db, populate_db
    ):
        # Создаем двух пользователей и экзамен
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
                    "email": "test2@example.com",
                    "user_name": "Test2",
                    "password_hash": "hash2",
                },
            ],
            exams=[{"id": 1, "title": "Test Exam", "creator_id": 1}],
        )

        result = UserRepo.check_that_user_is_creator(2, 1, test_db)

        assert result is False

    def test_check_that_user_is_creator_returns_false_when_exam_does_not_exist(
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
            ]
        )

        result = UserRepo.check_that_user_is_creator(1, 999, test_db)

        assert result is False


class TestUserRepoGetUserByEmail:
    @pytest.mark.parametrize(
        "user_id,email,user_name,password_hash",
        [
            (1, "test@example.com", "Test User", "hashed_password"),
            (2, "user2@example.com", "User Two", "hashed_password_2"),
            (3, "admin@example.com", "Admin User", "admin_hashed_password"),
        ],
    )
    def test_get_user_by_email_returns_user_when_exists(
        self, test_db, populate_db, user_id, email, user_name, password_hash
    ):
        populate_db(
            users=[
                {
                    "id": user_id,
                    "email": email,
                    "user_name": user_name,
                    "password_hash": password_hash,
                }
            ]
        )

        result = UserRepo.get_user_by_email(email, test_db)

        assert result.email == email
        assert result.id == user_id
        assert result.user_name == user_name

    def test_get_user_by_email_raises_exception_when_not_found(self, test_db):
        with pytest.raises(UserNotFound):
            UserRepo.get_user_by_email("nonexistent@example.com", test_db)

    def test_get_user_by_email_with_empty_string(self, test_db):
        with pytest.raises(UserNotFound):
            UserRepo.get_user_by_email("", test_db)


class TestUserRepoRegisterUser:
    @pytest.mark.parametrize(
        "user_id,email,user_name,password_hash",
        [
            (1, "test@example.com", "Test User", "hashed_password"),
            (2, "user2@example.com", "User Two", "hashed_password_2"),
            (3, "admin@example.com", "Admin User", "admin_hashed_password"),
        ],
    )
    def test_register_user_adds_user_to_database(
        self, test_db, user_id, email, user_name, password_hash
    ):
        new_user = User(
            id=user_id, email=email, user_name=user_name, password_hash=password_hash
        )

        result = UserRepo.register_user(new_user, test_db)

        assert result.id == user_id
        assert result.email == email
        assert result.user_name == user_name

        # Проверяем, что пользователь действительно в БД
        saved_user = test_db.query(User).filter(User.id == user_id).first()
        assert saved_user is not None
        assert saved_user.email == email

    def test_register_user_returns_user_with_id(self, test_db):
        new_user = User(
            id=42, email="new@example.com", user_name="New User", password_hash="hash"
        )

        result = UserRepo.register_user(new_user, test_db)

        assert result.id == 42
        assert result.email == "new@example.com"

    def test_register_user_persists_all_fields(self, test_db):
        new_user = User(
            id=1,
            email="fulluser@example.com",
            user_name="Full User",
            password_hash="hashed_password",
        )

        result = UserRepo.register_user(new_user, test_db)

        assert result.email == "fulluser@example.com"
        assert result.user_name == "Full User"
        assert result.password_hash == "hashed_password"

        # Проверяем в БД
        saved_user = test_db.query(User).filter(User.id == 1).first()
        assert saved_user.email == "fulluser@example.com"
        assert saved_user.user_name == "Full User"


class TestUserRepoGetUserById:
    def test_get_user_by_id_returns_user_when_exists(self, test_db, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "test@example.com",
                    "user_name": "Test",
                    "password_hash": "hash",
                }
            ]
        )

        user = UserRepo.get_user_by_id(1, test_db)

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.user_name == "Test"

    def test_get_user_by_id_raises_exception_when_not_found(self, test_db):
        with pytest.raises(UserNotFound):
            UserRepo.get_user_by_id(999, test_db)


class TestUserRepoUpdateUserToken:
    def test_update_user_token_updates_token(self, test_db, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "user@example.com",
                    "user_name": "User",
                    "password_hash": "hash",
                }
            ]
        )

        updated_user = UserRepo.update_user_token(1, "new_token", test_db)

        assert updated_user.auth_token == "new_token"

        # Проверяем в БД
        user_from_db = test_db.query(User).filter(User.id == 1).first()
        assert user_from_db.auth_token == "new_token"


class TestUserRepoRegisterPush:
    def test_register_push_sets_push_fields(self, test_db, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "push@example.com",
                    "user_name": "PushUser",
                    "password_hash": "hash",
                }
            ]
        )

        UserRepo.register_push(
            user_id=1,
            push_key="push_key_123",
            auth="auth_token_123",
            endpoint="endpoint_url",
            db=test_db,
        )

        user = test_db.query(User).filter(User.id == 1).first()

        assert user.push_key == "push_key_123"
        assert user.auth_token == "auth_token_123"
        assert user.endpoint == "endpoint_url"

    def test_register_push_raises_when_user_not_found(self, test_db):
        with pytest.raises(UserNotFound):
            UserRepo.register_push(
                user_id=999,
                push_key="push",
                auth="auth",
                endpoint="endpoint",
                db=test_db,
            )


class TestUserRepoUnregisterPush:
    def test_unregister_push_clears_push_fields(self, test_db, populate_db):
        populate_db(
            users=[
                {
                    "id": 1,
                    "email": "push@example.com",
                    "user_name": "PushUser",
                    "password_hash": "hash",
                    "push_key": "push_key",
                    "auth_token": "auth_token",
                    "endpoint": "endpoint",
                }
            ]
        )

        UserRepo.unregister_push(1, test_db)

        user = test_db.query(User).filter(User.id == 1).first()

        assert user.push_key is None
        assert user.auth_token is None
        assert user.endpoint is None

    def test_unregister_push_raises_when_user_not_found(self, test_db):
        with pytest.raises(UserNotFound):
            UserRepo.unregister_push(999, test_db)
