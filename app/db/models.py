from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str]
    is_verified: Mapped[bool] 
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    owned_clubs: Mapped[list["Club"]] = relationship(
        secondary="club_owners", back_populates="owners"
    )

class ClubOwner(Base):
    __tablename__ = "club_owners"
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

class Club(Base):
    __tablename__ = 'clubs'
    __table_args__ = (UniqueConstraint("name", name="uq_club_name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    owners: Mapped[list[User]] = relationship(
        secondary="club_owners", back_populates="owned_clubs"
    )
