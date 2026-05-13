from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str | None] = mapped_column(nullable=True)
    year: Mapped[str | None] = mapped_column(nullable=True)
    major: Mapped[str | None] = mapped_column(nullable=True)
    interests: Mapped[str | None] = mapped_column(nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

class Club(Base):
    __tablename__ = 'clubs'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    location: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

