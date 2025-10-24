from sqlalchemy.orm import Session
from infrastructure.user.user import User
from app.api.routes.auth import hash_password


def create_mock_users(db: Session):
    users = [
        User(
            email = "admin@test.com",
            user_name = "Test Name 1",
            password_hash = hash_password("testAdmin")
        ),
        User(
            email = "user1@test.com",
            user_name = "Test Name 2",
            password_hash = hash_password("testUser1")
        ),
        User(
            email = "user2@test.com",
            user_name = "Test Name 3",
            password_hash = hash_password("testUser2")
        ),
    ]

    db.add_all(users)
    db.commit()
