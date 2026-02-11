from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str]
    is_verified: Mapped[bool] 
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

class Club(Base):
    __tablename__ = 'clubs'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

