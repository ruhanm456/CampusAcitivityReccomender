from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, Text
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
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

class ClubMember(Base):
    __tablename__ = "club_members"
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

class Club(Base):
    __tablename__ = 'clubs'
    __table_args__ = (UniqueConstraint("name", name="uq_club_name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    meeting_time: Mapped[str | None] = mapped_column(nullable=True)
    location: Mapped[str | None] = mapped_column(nullable=True)
    members_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    owners: Mapped[list[User]] = relationship(
        secondary="club_owners", back_populates="owned_clubs"
    )
    hosted_events: Mapped[list["Event"]] = relationship(
        back_populates="host_club", cascade="all, delete-orphan", foreign_keys="Event.host"
    )

class Event(Base):
    __tablename__ = 'events'
    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    time: Mapped[datetime] = mapped_column(nullable=False)
    location: Mapped[str | None]
    host_club: Mapped["Club"] = relationship(back_populates="hosted_events")
    collaborations: Mapped[list[int]] = relationship(
        foreign_keys="Club.id", cascade="all, delete-orphan"
    )