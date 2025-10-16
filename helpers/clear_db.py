from infrastructure.database import SessionLocal
from infrastructure.models import User

db = SessionLocal()

try:
    db.query(User).delete()
    db.commit()
except Exception as e:
    db.rollback()
    print(f"Error in delete: {e}")
finally:
    db.close()