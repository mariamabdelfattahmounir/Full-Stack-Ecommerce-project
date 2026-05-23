
from sqlalchemy.orm import Session

from app.db.seed_service import SeedService


def init_db(db: Session) -> dict:
    service = SeedService(db)
    return service.seed_all()
