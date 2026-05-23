from app.db.session import engine
from app.db.base import Base

print("Dropping tables...")
Base.metadata.drop_all(bind=engine)

print("Creating tables...")
Base.metadata.create_all(bind=engine)

print("Database reset complete.")