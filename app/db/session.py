from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from CampusActivityReccomender.config import Config

engine_kwargs = {"future": True}
if Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, **engine_kwargs)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
