import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.models import Base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")

# For SQLite, disable thread checking to allow TestClient usage
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # All sessions use the same connection
)
Base.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session
