from sqlalchemy.orm import Session
from infrastructure.models import User
from app.api.routes.users import hash_password


def create_mock_users(db: Session):
    users = [
        User(
            login = "admin",
            user_name = "Test Name 1",
            password_hash = hash_password("testAdmin")
        ),
        User(
            login = "user1",
            user_name = "Test Name 2",
            password_hash = hash_password("testUser1")
        ),
        User(
            login = "user2",
            user_name = "Test Name 3",
            password_hash = hash_password("testUser2")
        ),
    ]

    db.add_all(users)
    db.commit()
