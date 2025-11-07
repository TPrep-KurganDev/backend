from tprep.infrastructure.database import SessionLocal
from tprep.infrastructure.user.user import User


def clear_db() -> None:
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error in delete: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    clear_db()
