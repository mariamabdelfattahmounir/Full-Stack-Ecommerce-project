import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.roles import Role
from app.core.security import get_password_hash
from app.models.user import User

logger = logging.getLogger(__name__)


def seed_initial_data(db: Session) -> None:
    logger.info("Starting initial seed process")

    existing_admin = db.scalar(select(User).where(User.email == "admin@example.com"))
    if existing_admin:
        logger.info("Admin user already exists, skipping seed")
        return

    admin_user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("Admin@123456"),
        full_name="System Administrator",
        role=Role.ADMIN,
        is_active=True,
        is_superuser=True,
    )

    db.add(admin_user)
    db.commit()
    logger.info("Initial admin user created successfully")