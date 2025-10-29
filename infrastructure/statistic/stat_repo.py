from fastapi import Depends
from sqlalchemy.orm import Session

from infrastructure.database import get_db
from infrastructure.statistic.statistic import Statistic


class StatRepo:
    @staticmethod
    def inc_mistakes(user_id: int, card_id: int, db: Session = Depends(get_db)) -> None:
        stat = db.query(Statistic).filter(
            Statistic.user_id == user_id,
            Statistic.card_id == card_id
        ).first()

        if stat:
            stat.mistakes_count += 1
        else:
            stat = Statistic(
                user_id=user_id,
                card_id=card_id,
                mistakes_count=1
            )
            db.add(stat)

        db.commit()